<template>
  <el-dialog
    v-model="dialogInboundView"
    title="Xem thông tin phiếu nhập"
    width="1100"
    destroy-on-close
  >
    <div class="dialog-header">
      <el-button type="primary" plain :loading="loading" @click="viewForm">
        Tải lại dữ liệu
      </el-button>
    </div>

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="mb-16"
    />

    <el-form :model="viewForm" label-width="140px" class="receipt-form">
      <el-row :gutter="16">
        <el-col :xs="24" :md="12">
          <el-form-item label="Mã kho">
            <el-input v-model="viewForm.code" placeholder="Chưa có dữ liệu" />
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-form-item label="Tên nhà kho">
            <el-input v-model="viewForm.name" placeholder="Chưa có dữ liệu" />
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-form-item label="Người quản lý">
            <el-input v-model="viewForm.manager_name" placeholder="Chưa có dữ liệu" />
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-form-item label="Địa chỉ">
            <el-input v-model="viewForm.address" placeholder="Chưa có dữ liệu" />
          </el-form-item>
        </el-col>

         <el-col :xs="24" :md="12">
          <el-form-item label="Trạng thái">
            <el-select
              v-model="viewForm.is_active"
              placeholder="Chưa chọn trạng thái"
              style="width: 100%"
            >
              <el-option
                v-for="status in statusOptions"
                :key="status.id"
                :label="status.name"
                :value="status.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :xs="24" :md="12">
          <el-form-item label="Tạo lúc">
            <el-date-picker
              v-model="viewForm.created_at"
              type="datetime"
              placeholder="Pick a Date"
              format="DD/MM/YYYY HH:mm:ss"
              value-format="DD/MM/YYYY HH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <!-- <el-col :xs="24" :md="12">
          <el-form-item label="Người duyệt">
            <el-input v-model="viewForm.approved_by" placeholder="Chưa có dữ liệu" readonly />
          </el-form-item>
        </el-col>

        <el-col :xs="24">
          <el-form-item label="Ghi chú">
            <el-input
              v-model="viewForm.note"
              type="textarea"
              :rows="3"
              placeholder="Chưa có ghi chú"
              readonly
            />
          </el-form-item>
        </el-col> -->
      </el-row>

      <!-- <div class="items-header">
        <h3>Chi tiết hàng nhập</h3>
        <el-tag type="info" effect="light">
          {{ productItems.length }} dòng sản phẩm từ DB
        </el-tag>
      </div>

      <div
        v-for="(item, index) in productItems"
        :key="item.id || index"
        class="item-card"
      >
        <div class="item-card__header">
          <span>Dòng hàng #{{ index + 1 }}</span>
        </div>

        <el-row :gutter="16">
          <el-col :xs="24" :md="8">
            <el-form-item label="Sản phẩm" label-width="120px">
              <el-input :model-value="String(item.id ?? '')" readonly />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="8">
            <el-form-item label="SKU SP" label-width="120px">
              <el-input :model-value="item.sku || ''" placeholder="Không có SKU" readonly />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="8">
            <el-form-item label="Batch" label-width="120px">
              <el-input :model-value="item.batch || ''" placeholder="Chưa có batch" readonly />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="8">
            <el-form-item label="Mã batch" label-width="120px">
              <el-input :model-value="item.batch_no || ''" placeholder="Chưa có mã batch" readonly />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="8">
            <el-form-item label="Số lượng" label-width="120px">
              <el-input :model-value="String(item.quantity ?? 0)" readonly />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="8">
            <el-form-item label="Đơn giá nhập" label-width="120px">
              <el-input :model-value="String(item.price ?? 0)" readonly />
            </el-form-item>
          </el-col>

          <el-col :xs="24">
            <el-form-item label="Ghi chú dòng" label-width="120px">
              <el-input
                :model-value="item.name || ''"
                type="textarea"
                :rows="2"
                placeholder="Không có ghi chú"
                readonly
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <el-empty
        v-if="!loading && productItems.length === 0"
        description="Không có sản phẩm nào từ database"
      />

      <div class="audit-grid">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item label="Người tạo">
              <el-input v-model="viewForm.created_by" placeholder="Chưa có dữ liệu" readonly />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="Người cập nhật">
              <el-input v-model="viewForm.updated_by" placeholder="Chưa có dữ liệu" readonly />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="Tạo lúc">
              <el-input v-model="viewForm.created_at" placeholder="Chưa có dữ liệu" readonly />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item label="Cập nhật lúc">
              <el-input v-model="viewForm.updated_at" placeholder="Chưa có dữ liệu" readonly />
            </el-form-item>
          </el-col>
        </el-row>
      </div> -->
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogInboundView = false">Đóng</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { useWarehouse } from '@/composables/ware-house.composable';

const statusOptions = [
  { id: true, name: 'Đang hoạt động' },
  { id: false, name: 'Ngừng hoạt động' },
]
const dialogInboundView = defineModel<boolean>('dialogInboundView', {
  default: false,
})
interface Props {
  error?: boolean;
  loading?: boolean;
}
const props = defineProps<Props>();

  const { warehouse } = useWarehouse();
  const viewForm = warehouse.value;
</script>

<style scoped>
.receipt-form {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 8px;
}

.dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.dialog-description {
  margin: 0;
  color: var(--el-text-color-secondary);
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

.mb-16 {
  margin-bottom: 16px;
}
</style>