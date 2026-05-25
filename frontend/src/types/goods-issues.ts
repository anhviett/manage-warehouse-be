export type GoodsIssueItemForm = {
  goods_issue: string | number
  issue_no: string
  product: string | number
  product_sku: string
  batch: string | number
  batch_no: string
  quantity: number
  unit_price: number
  note: string
  created_by: string | number
  updated_by: string | number
  created_at: string
  updated_at: string
}

export type GoodsIssueForm = {
  id: string | number
  issue_no: string
  warehouse: string | number
  warehouse_code: string
  customer_name: string
  reference_no: string
  issued_at: string
  status: 'DRAFT' | 'POSTED' | 'CANCELLED'
  note: string
  approved_by: string | number
  created_by: string | number
  updated_by: string | number
  created_at: string
  updated_at: string
  items: GoodsIssueItemForm[]
}