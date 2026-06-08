import { api } from '@/services/api'

export type InventoryQrResponse = {
  label: string
  payload: Record<string, unknown>
  image_base64: string
}

export function getInventoryQr(inventoryId: number | string) {
  return api.get<InventoryQrResponse>(`/inventories/${inventoryId}/qr/`)
}