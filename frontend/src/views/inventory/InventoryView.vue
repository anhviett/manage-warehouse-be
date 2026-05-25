<script setup lang="ts">
const warehouseStock = [
  { zone: 'A1', sku: 'SP-001', name: 'Máy quét mã vạch Zebra DS2208', onHand: 42, reserved: 6 },
  { zone: 'B2', sku: 'SP-014', name: 'Kệ sắt 5 tầng tải trọng 300kg', onHand: 16, reserved: 2 },
  { zone: 'C3', sku: 'SP-028', name: 'Tem nhãn in nhiệt 100x150', onHand: 8, reserved: 3 },
  { zone: 'D1', sku: 'SP-035', name: 'Màng PE quấn pallet', onHand: 76, reserved: 14 },
]
</script>

<template>
  <el-row :gutter="16">
    <el-col :xs="24" :lg="16">
      <el-card class="content-card">
        <template #header>
          <div>
            <h2 class="page-title">Tồn kho theo vị trí</h2>
            <p class="page-subtitle">Theo dõi số lượng thực tế và đã giữ chỗ theo từng khu vực</p>
          </div>
        </template>

        <el-table :data="warehouseStock" stripe>
          <el-table-column prop="zone" label="Khu vực" width="100" />
          <el-table-column prop="sku" label="SKU" width="120" />
          <el-table-column prop="name" label="Tên hàng" min-width="240" />
          <el-table-column prop="onHand" label="Tồn thực tế" width="120" />
          <el-table-column prop="reserved" label="Đã giữ" width="100" />
          <el-table-column label="Khả dụng" width="120">
            <template #default="{ row }">{{ row.onHand - row.reserved }}</template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-col>

    <el-col :xs="24" :lg="8">
      <el-card class="content-card">
        <template #header>
          <h3 class="page-title">Cảnh báo tồn kho</h3>
        </template>
        <el-alert title="SP-028 dưới mức tồn tối thiểu (10)" type="warning" :closable="false" show-icon />
        <el-alert
          class="mt-12"
          title="SP-041 chưa cập nhật vị trí lưu kho"
          type="error"
          :closable="false"
          show-icon
        />
        <el-divider />
        <el-progress :percentage="82" status="success">
          <span>Tỷ lệ đầy kho: 82%</span>
        </el-progress>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.mt-12 {
  margin-top: 12px;
}
</style>