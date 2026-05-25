import { defineStore } from 'pinia'
import type {  WareHouseGenaral, WareHouseProduct } from '@/types/warehouse.type'

export interface WarehouseState {
    wareHouseGenaral: WareHouseGenaral
    wareHouseProduct: WareHouseProduct
}

export const useWarehouseStore = defineStore('warehouse-store', () => {
    state: (): WarehouseState => ({
        wareHouseGenaral: {
            id: '',
            code: '',
            name: '',
            address: '',
            manager_name: '',
            is_active: true,
            created_at: '',
            updated_at: '',
        },
        wareHouseProduct: {
            id: '',
            receipt_no: '',
            warehouse: '',
            warehouse_code: '',
            supplier: '',
            supplier_name: '',
            supplier_code: '',
            supplier_address: '',
            supplier_phone: '',
            supplier_email: '',
            supplier_status: '',
            reference_no: '',
            received_at: '',
            status: 'DRAFT',
            note: '',
            approved_by: '',
            created_by: '',
            updated_by: '',
            created_at: '',
            updated_at: '',
        }
    })
})