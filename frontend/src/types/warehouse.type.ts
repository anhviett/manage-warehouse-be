export interface WareHouseGenaral {
  id: number | string
  code: string
  name: string
  address: string
  manager_name: string
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface WareHouseProduct {
  id: number | string
  receipt_no: string
  warehouse: string
  warehouse_code: string
  supplier: string
  supplier_name: string
  supplier_code: string
  supplier_address: string
  supplier_phone: string
  supplier_email: string
  supplier_status: string
  reference_no: string
  received_at: string
  status: 'DRAFT' | 'APPROVED' | 'REJECTED'
  note: string
  approved_by: string
  created_by: string
  updated_by: string
  created_at?: string
  updated_at?: string
}