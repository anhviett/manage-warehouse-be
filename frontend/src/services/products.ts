import { api } from '@/services/api';
export type ProductApiItem = {
  id: number | string
  sku: string
  name: string
  category_name: string | null
  supplier_name: string | null
  unit: string
  selling_price: number | string
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export function getProducts() {
  return api.get<ProductApiItem[]>('/products')
}

export function createProduct(payload: { name: string; price: number }) {
  return api.post('/products', payload)
}

export function getProductById(id: number) {
  return api.get<ProductApiItem>(`/products/${id}`)
}