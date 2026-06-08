from __future__ import annotations

from typing import Any

import pandas as pd
from django.db.models import Sum
from prophet import Prophet

from warehouse.models import Inventory, Product, StockMovement


def _build_daily_demand_frame(product_id: int, warehouse_id: int | None = None) -> pd.DataFrame:
    queryset = StockMovement.objects.filter(
        product_id=product_id,
        movement_type=StockMovement.MOVEMENT_OUT,
    )

    if warehouse_id is not None:
        queryset = queryset.filter(warehouse_id=warehouse_id)

    daily_data = (
        queryset.values("movement_at__date")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("movement_at__date")
    )

    df = pd.DataFrame(list(daily_data))
    if df.empty:
        return pd.DataFrame(columns=["ds", "y"])

    df = df.rename(columns={"movement_at__date": "ds", "total_quantity": "y"})
    df["ds"] = pd.to_datetime(df["ds"])
    df["y"] = df["y"].fillna(0).astype(float)
    return df


def forecast_product_demand(
    product_id: int,
    periods: int = 30,
    warehouse_id: int | None = None,
) -> dict[str, Any]:
    product = Product.objects.get(pk=product_id)
    history_df = _build_daily_demand_frame(product_id=product_id, warehouse_id=warehouse_id)

    if history_df.empty or len(history_df) < 2:
        inventory_queryset = Inventory.objects.filter(product_id=product_id)
        if warehouse_id is not None:
            inventory_queryset = inventory_queryset.filter(warehouse_id=warehouse_id)

        current_stock = sum(item.available_quantity for item in inventory_queryset)
        return {
            "product_id": product.id,
            "product_sku": product.sku,
            "product_name": product.name,
            "warehouse_id": warehouse_id,
            "periods": periods,
            "model": "fallback",
            "insufficient_history": True,
            "history_points": len(history_df.index),
            "forecast": [],
            "summary": {
                "current_stock": current_stock,
                "avg_daily_demand": 0,
                "predicted_total_demand": 0,
                "recommended_reorder_level": 0,
                "recommended_safety_stock": 0,
                "stockout_risk": "unknown",
            },
        }

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
    )
    model.fit(history_df)

    future = model.make_future_dataframe(periods=periods)
    forecast_df = model.predict(future).tail(periods).copy()

    inventory_queryset = Inventory.objects.filter(product_id=product_id)
    if warehouse_id is not None:
        inventory_queryset = inventory_queryset.filter(warehouse_id=warehouse_id)

    current_stock = sum(item.available_quantity for item in inventory_queryset)
    avg_daily_demand = float(history_df["y"].mean()) if not history_df.empty else 0
    predicted_total_demand = float(forecast_df["yhat"].clip(lower=0).sum())
    recommended_safety_stock = max(round(avg_daily_demand * 7), 0)
    recommended_reorder_level = max(round(avg_daily_demand * 14), 0)

    if predicted_total_demand <= 0:
        stockout_risk = "low"
    elif current_stock <= recommended_safety_stock:
        stockout_risk = "high"
    elif current_stock <= recommended_reorder_level:
        stockout_risk = "medium"
    else:
        stockout_risk = "low"

    forecast_records = []
    for row in forecast_df.itertuples(index=False):
        forecast_records.append(
            {
                "ds": pd.Timestamp(row.ds).date().isoformat(),
                "yhat": max(float(row.yhat), 0.0),
                "yhat_lower": max(float(row.yhat_lower), 0.0),
                "yhat_upper": max(float(row.yhat_upper), 0.0),
            }
        )

    return {
        "product_id": product.id,
        "product_sku": product.sku,
        "product_name": product.name,
        "warehouse_id": warehouse_id,
        "periods": periods,
        "model": "prophet",
        "insufficient_history": False,
        "history_points": len(history_df.index),
        "forecast": forecast_records,
        "summary": {
            "current_stock": current_stock,
            "avg_daily_demand": round(avg_daily_demand, 2),
            "predicted_total_demand": round(predicted_total_demand, 2),
            "recommended_reorder_level": recommended_reorder_level,
            "recommended_safety_stock": recommended_safety_stock,
            "stockout_risk": stockout_risk,
        },
    }