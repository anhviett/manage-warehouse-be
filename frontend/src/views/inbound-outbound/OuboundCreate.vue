<template>
  <el-dialog
    v-model="dialogOutboundCreate"
    title="Tạo phiếu xuất kho"
    width="1100"
    destroy-on-close
  >
    <el-form :model="form" label-width="140px" class="issue-form">
      <el-row :gutter="16">
        <el-col :xs="24" :md="12">
          <el-form-item label="Số phiếu xuất">
            <el-input v-model="form.issue_no" placeholder="Nhập số phiếu xuất" />
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-form-item label="Kho">
            <el-select
              v-model="form.warehouse"
              placeholder="Chọn kho"
              style="width: 100%"
              clearable
            >
              <el-option
                v-for="warehouse in warehouseOptions"
                :key="warehouse.id"
                :label="`${warehouse.code} - ${warehouse.name}`"
                :value="warehouse.id"
              />
            </el-select>
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-form-item label="Tên khách hàng">
            <el-input v-model="form.customer_name" placeholder="Nhập tên khách hàng" />
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-form-item label="Mã kho">
            <el-input v-model="form.warehouse_code" placeholder="warehouse_code" readonly />
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-form-item label="Số tham chiếu">
            <el-input v-model="form.reference_no" placeholder="Nhập số tham chiếu" />
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-form-item label="Ngày xuất">
            <el-date-picker
              v-model="form.issued_at"
              type="datetime"
              placeholder="Chọn ngày xuất"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-form-item label="Trạng thái">
            <el-select v-model="form.status" placeholder="Chọn trạng thái" style="width: 100%">
              <el-option label="Nháp" value="DRAFT" />
              <el-option label="Đã ghi sổ" value="POSTED" />
              <el-option label="Đã hủy" value="CANCELLED" />
            </el-select>
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-form-item label="Người duyệt">
            <el-input v-model="form.approved_by" placeholder="Nhập ID người duyệt" />
          </el-form-item>
        </el-col>

        <el-col :xs="24">
          <el-form-item label="Ghi chú">
            <el-input
              v-model="form.note"
              type="textarea"
              :rows="3"
              placeholder="Nhập ghi chú phiếu xuất"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <div class="items-header">
        <h3>Chi tiết hàng xuất</h3>
        <el-button type="primary" plain @click="addItem">+ Thêm dòng hàng</el-button>
      </div>

      <div
        v-for="(item, index) in form.items"
        :key="index"
        class="item-card"
      >
        <div class="item-card__header">
          <span>Dòng hàng #{{ index + 1 }}</span>
          <el-button
            type="danger"
            text
            @click="removeItem(index)"
            :disabled="form.items.length === 1"
          >
            Xóa
          </el-button>
        </div>

        <el-row :gutter="16">
          <el-col :xs="24" :md="8">
            <el-form-item label="Sản phẩm" label-width="120px">
              <el-input v-model="item.product" placeholder="Nhập ID sản phẩm" />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="8">
            <el-form-item label="SKU SP" label-width="120px">
              <el-input v-model="item.product_sku" placeholder="SKU sản phẩm" readonly />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="8">
            <el-form-item label="Batch" label-width="120px">
              <el-input v-model="item.batch" placeholder="Nhập ID batch" />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="8">
            <el-form-item label="Mã batch" label-width="120px">
              <el-input v-model="item.batch_no" placeholder="Mã batch" readonly />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="8">
            <el-form-item label="Số lượng" label-width="120px">
              <el-input-number v-model="item.quantity" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="8">
            <el-form-item label="Đơn giá xuất" label-width="120px">
              <el-input-number
                v-model="item.unit_price"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <el-col :xs="24">
            <el-form-item label="Ghi chú dòng" label-width="120px">
              <el-input
                v-model="item.note"
                type="textarea"
                :rows="2"
                placeholder="Ghi chú cho dòng hàng"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <div class="audit-grid">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item label="Người tạo">
              <el-input v-model="form.created_by" placeholder="ID người tạo" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="Người cập nhật">
              <el-input v-model="form.updated_by" placeholder="ID người cập nhật" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="Tạo lúc">
              <el-input v-model="form.created_at" placeholder="created_at" readonly />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="Cập nhật lúc">
              <el-input v-model="form.updated_at" placeholder="updated_at" readonly />
            </el-form-item>
          </el-col>
        </el-row>
      </div>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogOutboundCreate = false">Hủy</el-button>
        <el-button type="primary">Lưu phiếu xuất</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { computed, reactive } from 'vue'
import { useWarehouse } from '@/composables/ware-house.composable'
import type { GoodsIssueForm, GoodsIssueItemForm } from '@/types/goods-issues'

const dialogOutboundCreate = defineModel<boolean>('dialogOutboundCreate', {
  default: false,
})

const warehouseStore = useWarehouse()

const warehouseOptions = computed(() => warehouseStore.warehouses)

function createEmptyItem(): GoodsIssueItemForm {
  return {
    goods_issue: '',
    issue_no: '',
    product: '',
    product_sku: '',
    batch: '',
    batch_no: '',
    quantity: 1,
    unit_price: 0,
    note: '',
    created_by: '',
    updated_by: '',
    created_at: '',
    updated_at: '',
  }
}

const form = reactive<GoodsIssueForm>({
  id: '',
  issue_no: '',
  warehouse: '',
  warehouse_code: '',
  customer_name: '',
  reference_no: '',
  issued_at: '',
  status: 'DRAFT',
  note: '',
  approved_by: '',
  created_by: '',
  updated_by: '',
  created_at: '',
  updated_at: '',
  items: [createEmptyItem()],
})

function addItem() {
  form.items.push(createEmptyItem())
}

function removeItem(index: number) {
  if (form.items.length === 1) return
  form.items.splice(index, 1)
}
</script>

<style scoped>
.issue-form {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 8px;
}

.items-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 12px 0 16px;
}

.item-card {
  border: 1px solid var(--el-border-color);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  background: var(--el-fill-color-blank);
}

.item-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  font-weight: 600;
}

.audit-grid {
  margin-top: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>