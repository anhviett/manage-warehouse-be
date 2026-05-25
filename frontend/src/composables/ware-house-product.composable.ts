import { ref } from 'vue'
import { getProducts, getProductById } from '@/services/products'
import type { WareHouseProduct } from '@/types/warehouse.type'

export function useWareHouseProduct() {
    const products = ref<WareHouseProduct[]>([]);
    const product = ref<WareHouseProduct | null>(null)
    const loading = ref(false)
    const error = ref<string | null>(null)
    async function fetchWareHouseProducts() {
        loading.value = true
        error.value = null
        try {
            const data = await getProducts()
            products.value = Array.isArray(data) ? data : []
        } catch (err) {
            console.log('err: ', err);
            error.value = err instanceof Error ? err.message : 'Failed to fetch warehouse products'
        } finally {
            loading.value = false
        }
    }

    async function fetchWareHouseProductById(id: number) {
        loading.value = true
        error.value = null
        try {
            const data = await getProductById(id)

            if (data) {
                product.value = data
            }
        } catch (err) {
            console.log('err: ', err);
            error.value = err instanceof Error ? err.message : `Failed to fetch warehouse product with ID ${id}`
        } finally {
            loading.value = false
        }
    }

    return {
        products,
        product,
        loading,
        error,
        fetchWareHouseProducts,
        fetchWareHouseProductById
    }
}