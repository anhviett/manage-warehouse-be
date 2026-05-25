<script setup lang="ts">
const summary = [
  { label: 'Tổng nhập tháng này', value: '4,820 đơn vị' },
  { label: 'Tổng xuất tháng này', value: '4,265 đơn vị' },
  { label: 'Tỷ lệ hoàn thành đơn', value: '97.4%' },
  { label: 'Sai lệch kiểm kho', value: '0.8%' },
]

const topProducts = [
  { name: 'Máy quét mã vạch Zebra DS2208', outbound: 320, revenue: '944.000.000 đ' },
  { name: 'Màng PE quấn pallet', outbound: 280, revenue: '112.000.000 đ' },
  { name: 'Tem nhãn in nhiệt 100x150', outbound: 250, revenue: '46.250.000 đ' },
]
</script>

<template>
  <div class="reports-page">
    <el-row :gutter="16">
      <el-col v-for="item in summary" :key="item.label" :xs="24" :sm="12" :lg="6">
        <el-card class="content-card stat-card" shadow="hover">
          <p class="label">{{ item.label }}</p>
          <h3 class="value">{{ item.value }}</h3>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-16">
      <el-col :xs="24" :lg="14">
        <el-card class="content-card">
          <template #header>
            <h2 class="page-title">Top sản phẩm xuất kho</h2>
          </template>
          <el-table :data="topProducts" stripe>
            <el-table-column prop="name" label="Sản phẩm" min-width="250" />
            <el-table-column prop="outbound" label="SL xuất" width="120" />
            <el-table-column prop="revenue" label="Doanh thu nội bộ" width="180" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="content-card">
          <template #header>
            <h2 class="page-title">Xuất báo cáo</h2>
          </template>
          <p class="page-subtitle">Tạo file báo cáo nhanh cho kế toán/vận hành</p>
          <el-form label-position="top">
            <el-form-item label="Loại báo cáo">
              <el-select placeholder="Chọn loại báo cáo">
                <el-option label="Báo cáo tồn kho" value="inventory" />
                <el-option label="Báo cáo nhập xuất" value="inout" />
                <el-option label="Báo cáo hiệu suất kho" value="performance" />
              </el-select>
            </el-form-item>
            <el-form-item label="Định dạng">
              <el-radio-group>
                <el-radio value="xlsx">Excel (.xlsx)</el-radio>
                <el-radio value="csv">CSV (.csv)</el-radio>
                <el-radio value="pdf">PDF (.pdf)</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-button type="primary">Xuất báo cáo</el-button>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.stat-card {
  margin-bottom: 16px;
}
.label {
  margin: 0;
  color: var(--text-secondary);
}
.value {
  margin: 10px 0 0;
  font-size: 24px;
}
.mt-16 {
  margin-top: 0;
}
</style>