<script setup lang="ts">
import { onMounted, ref } from 'vue'
import InboundCreate from '@/views/inbound-outbound/inbound/InboundCreate.vue';
import InboundView from '@/views/inbound-outbound/inbound/InboundView.vue';
import { useWarehouse } from '@/composables/ware-house.composable'

const dialogInboundCreate = ref(false);
const inboundView = ref(false);
const dialogOutboundCreate = ref(false);
const selectedWarehouse = ref<number | string | undefined>()

const { warehouses, fetchWarehouses, fetchWarehouseById, loading: warehouseLoading } = useWarehouse();
onMounted(() => {
  fetchWarehouses()
})

const showInboundView = async (warehouseId: number) => {
  await fetchWarehouseById(warehouseId)
  inboundView.value = true
}

const approveInbound = (warehouseId: number) => {
  // placeholder approval handler
  // implement API call or dialog open as needed
  console.log('approve inbound for warehouse:', warehouseId)
}

</script>

<template>
  <el-card class="content-card">
    <template #header>
      <div>
        <h2 class="page-title">Nhập / Xuất kho</h2>
        <p class="page-subtitle">Theo dõi luồng hàng hóa vào ra và trạng thái xử lý chứng từ</p>
      </div>
    </template>

    <el-row :gutter="12" class="filters">
      <el-col :xs="24" :md="6">
        <el-date-picker type="daterange" start-placeholder="Từ ngày" end-placeholder="Đến ngày" style="width: 100%" />
      </el-col>
      <el-col :xs="24" :md="6">
        <el-select placeholder="Loại phiếu" style="width: 100%">
          <el-option label="Tất cả" value="all" />
          <el-option label="Nhập kho" value="inbound" />
          <el-option label="Xuất kho" value="outbound" />
        </el-select>
      </el-col>
      <el-col :xs="24" :md="6">
        <el-select
          v-model="selectedWarehouse"
          placeholder="Chọn kho"
          style="width: 100%"
          :loading="warehouseLoading"
          clearable
        >
          <el-option
            v-for="warehouse in warehouses"
            :key="warehouse.id"
            :label="`${warehouse.code} - ${warehouse.name}`"
            :value="warehouse.id"
          />
        </el-select>
      </el-col>
      <el-col :xs="24" :md="6">
        <div class="actions">
          <el-button type="success" @click="dialogInboundCreate = true">+ Tạo phiếu nhập</el-button>
          <el-button type="primary" @click="dialogOutboundCreate = true">+ Tạo phiếu xuất</el-button>
        </div>
      </el-col>
    </el-row>

    <el-table :data="warehouses" stripe v-loading="warehouseLoading">
      <el-table-column prop="id" label="ID kho" width="100" />
      <el-table-column prop="code" label="Mã kho" width="140" />
      <el-table-column prop="name" label="Tên kho" min-width="220" />
      <el-table-column prop="address" label="Địa chỉ" min-width="260" />
      <el-table-column prop="manager_name" label="Quản lý kho" min-width="180" />
      <el-table-column label="Trạng thái" width="120">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" effect="light">
            {{ row.is_active ? 'Đang hoạt động' : 'Ngừng hoạt động' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Thao tác" width="150">
        <template #default="{ row }">
          <el-button size="small" text type="primary" @click="showInboundView(row.id)">Xem</el-button>
          <el-button size="small" text type="warning" @click="approveInbound(row.id)">Duyệt</el-button>  
        </template>
      </el-table-column>
    </el-table>
  </el-card>
  <InboundCreate v-model:dialogInboundCreate="dialogInboundCreate" />
  <InboundView v-model:dialogInboundView="inboundView" />
</template>

<style scoped>
.filters {
  margin-bottom: 14px;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.actions :deep(.el-button) {
  margin-left: 0;
}

@media (max-width: 991px) {
  .actions {
    justify-content: flex-start;
    margin-top: 8px;
  }
}
</style>