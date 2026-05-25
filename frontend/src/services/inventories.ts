import { api } from '@/services/api'

export type InventoryQrResponse = {
  qr_code?: string
  qr_image?: string
  qr_url?: string
  image?: string
  data?: string
  [key: string]: unknown
}

export function getInventoryQr(inventoryId: number | string) {
  return api.get<InventoryQrResponse>(`/inventories/${inventoryId}/qr/`)
}