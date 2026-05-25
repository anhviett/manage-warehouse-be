import { ref } from 'vue'
import { getWarehouseById, getWarehouses } from '@/services/warehouses'
import type { WareHouseGenaral } from '@/types/warehouse.type'

export function useWarehouse() {
    const warehouses = ref<WareHouseGenaral[]>([]);
    const warehouse = ref<WareHouseGenaral | null>(null)
    const loading = ref(false)
    const error = ref<string | null>(null)

    async function fetchWarehouses() {
        loading.value = true
        error.value = null

        try {
            const data = await getWarehouses()
            warehouses.value = Array.isArray(data) ? data : []
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to fetch warehouses'
        } finally {
            loading.value = false
        }
    }

    async function fetchWarehouseById(id: number) {
        loading.value = true
        error.value = null

        try {
            const data = await getWarehouseById(id)
            warehouse.value = data;
        } catch (err) {
            error.value = err instanceof Error ? err.message : `Failed to fetch warehouse with ID ${id}`
        } finally {
            loading.value = false
        }
    }

    return {
        warehouses,
        warehouse,
        loading,
        error,
        fetchWarehouses,
        fetchWarehouseById
    }
}