from __future__ import annotations

from typing import Any

from ortools.linear_solver import pywraplp

from warehouse.models import Product, Shelf


def optimize_shelf_space(
    *,
    shelf_ids: list[int],
    item_requests: list[dict[str, int]],
) -> dict[str, Any]:
    shelves = list(Shelf.objects.filter(id__in=shelf_ids, is_active=True).select_related("warehouse"))
    if not shelves:
        return {
            "status": "error",
            "message": "Không tìm thấy kệ hợp lệ để tối ưu.",
            "allocation": [],
            "unassigned_items": item_requests,
            "summary": {
                "requested_items": len(item_requests),
                "assigned_items": 0,
                "used_shelves": 0,
            },
        }

    expanded_items: list[dict[str, Any]] = []
    for request in item_requests:
        product = Product.objects.get(pk=request["product_id"])
        quantity = int(request.get("quantity", 0))
        for unit_index in range(quantity):
            expanded_items.append(
                {
                    "product_id": product.id,
                    "sku": product.sku,
                    "name": product.name,
                    "volume": float(product.volume),
                    "weight": float(product.weight),
                    "request_quantity": quantity,
                    "unit_index": unit_index,
                }
            )

    if not expanded_items:
        return {
            "status": "success",
            "message": "Không có mặt hàng nào cần sắp xếp.",
            "allocation": [],
            "unassigned_items": [],
            "summary": {
                "requested_items": 0,
                "assigned_items": 0,
                "used_shelves": 0,
            },
        }

    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        return _heuristic_slotting(shelves=shelves, expanded_items=expanded_items)

    num_items = len(expanded_items)
    num_shelves = len(shelves)

    x = {}
    for i in range(num_items):
        for j in range(num_shelves):
            x[i, j] = solver.IntVar(0, 1, f"item_{i}_shelf_{j}")

    y = [solver.IntVar(0, 1, f"shelf_used_{j}") for j in range(num_shelves)]

    for i in range(num_items):
        solver.Add(sum(x[i, j] for j in range(num_shelves)) <= 1)

    for j, shelf in enumerate(shelves):
        solver.Add(
            sum(x[i, j] * expanded_items[i]["volume"] for i in range(num_items)) <= y[j] * shelf.volume
        )
        solver.Add(
            sum(x[i, j] * expanded_items[i]["weight"] for i in range(num_items)) <= y[j] * max(shelf.max_weight, 1_000_000)
        )

    penalty = solver.Sum(1 - solver.Sum(x[i, j] for j in range(num_shelves)) for i in range(num_items))
    solver.Minimize((1000 * solver.Sum(y)) + penalty)

    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL:
        return _heuristic_slotting(shelves=shelves, expanded_items=expanded_items)

    return _build_slotting_response(shelves=shelves, expanded_items=expanded_items, x=x, y=y)


def _build_slotting_response(*, shelves, expanded_items, x, y) -> dict[str, Any]:
    allocation = []
    assigned_count = 0
    unassigned_items = []

    for shelf_index, shelf in enumerate(shelves):
        if y[shelf_index].solution_value() <= 0:
            continue

        assigned_units = []
        used_volume = 0.0
        used_weight = 0.0

        for item_index, item in enumerate(expanded_items):
            if x[item_index, shelf_index].solution_value() > 0:
                assigned_units.append(
                    {
                        "product_id": item["product_id"],
                        "sku": item["sku"],
                        "name": item["name"],
                        "volume": item["volume"],
                        "weight": item["weight"],
                    }
                )
                used_volume += item["volume"]
                used_weight += item["weight"]
                assigned_count += 1

        allocation.append(
            {
                "shelf_id": shelf.id,
                "shelf_code": shelf.code,
                "warehouse_id": shelf.warehouse_id,
                "warehouse_code": shelf.warehouse.code,
                "used_volume": round(used_volume, 2),
                "max_volume": round(float(shelf.volume), 2),
                "used_weight": round(used_weight, 2),
                "max_weight": round(float(shelf.max_weight), 2),
                "utilization_rate": round((used_volume / shelf.volume) if shelf.volume else 0, 4),
                "items": assigned_units,
            }
        )

    for item_index, item in enumerate(expanded_items):
        assigned = any(x[item_index, shelf_index].solution_value() > 0 for shelf_index in range(len(shelves)))
        if not assigned:
            unassigned_items.append(
                {
                    "product_id": item["product_id"],
                    "sku": item["sku"],
                    "name": item["name"],
                    "volume": item["volume"],
                    "weight": item["weight"],
                }
            )

    return {
        "status": "success" if not unassigned_items else "partial",
        "message": "Tối ưu vị trí lưu trữ hoàn tất.",
        "allocation": allocation,
        "unassigned_items": unassigned_items,
        "summary": {
            "requested_items": len(expanded_items),
            "assigned_items": assigned_count,
            "used_shelves": len(allocation),
        },
    }


def _heuristic_slotting(*, shelves, expanded_items) -> dict[str, Any]:
    sorted_shelves = sorted(shelves, key=lambda shelf: shelf.volume, reverse=True)
    shelf_states = {
        shelf.id: {
            "remaining_volume": float(shelf.volume),
            "remaining_weight": float(shelf.max_weight or 1_000_000),
            "items": [],
            "shelf": shelf,
        }
        for shelf in sorted_shelves
    }

    unassigned_items = []
    for item in sorted(expanded_items, key=lambda candidate: candidate["volume"], reverse=True):
        placed = False
        for shelf in sorted_shelves:
            state = shelf_states[shelf.id]
            if (
                state["remaining_volume"] >= item["volume"]
                and state["remaining_weight"] >= item["weight"]
            ):
                state["remaining_volume"] -= item["volume"]
                state["remaining_weight"] -= item["weight"]
                state["items"].append(item)
                placed = True
                break

        if not placed:
            unassigned_items.append(
                {
                    "product_id": item["product_id"],
                    "sku": item["sku"],
                    "name": item["name"],
                    "volume": item["volume"],
                    "weight": item["weight"],
                }
            )

    allocation = []
    assigned_count = 0
    for shelf in sorted_shelves:
        state = shelf_states[shelf.id]
        if not state["items"]:
            continue

        used_volume = float(shelf.volume) - state["remaining_volume"]
        used_weight = float(shelf.max_weight or 1_000_000) - state["remaining_weight"]
        assigned_count += len(state["items"])

        allocation.append(
            {
                "shelf_id": shelf.id,
                "shelf_code": shelf.code,
                "warehouse_id": shelf.warehouse_id,
                "warehouse_code": shelf.warehouse.code,
                "used_volume": round(used_volume, 2),
                "max_volume": round(float(shelf.volume), 2),
                "used_weight": round(used_weight, 2),
                "max_weight": round(float(shelf.max_weight), 2),
                "utilization_rate": round((used_volume / shelf.volume) if shelf.volume else 0, 4),
                "items": [
                    {
                        "product_id": item["product_id"],
                        "sku": item["sku"],
                        "name": item["name"],
                        "volume": item["volume"],
                        "weight": item["weight"],
                    }
                    for item in state["items"]
                ],
            }
        )

    return {
        "status": "success" if not unassigned_items else "partial",
        "message": "Tối ưu vị trí lưu trữ hoàn tất bằng heuristic fallback.",
        "allocation": allocation,
        "unassigned_items": unassigned_items,
        "summary": {
            "requested_items": len(expanded_items),
            "assigned_items": assigned_count,
            "used_shelves": len(allocation),
        },
    }