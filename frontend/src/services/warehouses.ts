import { api } from '@/services/api'

export type WarehousePayload = {
  code: string
  name: string
  address?: string
  manager_name?: string
  is_active?: boolean
}

export function getWarehouses() {
  return api.get('/warehouses')
}

export function createWarehouse(payload: WarehousePayload) {
  return api.post('/warehouses', payload)
}

export function getWarehouseById(id?: number) {
  return api.get(`/warehouses/${id}`)
}
