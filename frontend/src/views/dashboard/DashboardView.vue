<script setup lang="ts">
import { ArrowDown, ArrowUp } from '@element-plus/icons-vue'

const kpiCards = [
  {
    title: 'Tổng SKU',
    value: '1,248',
    change: '+6.2%',
    up: true,
    color: 'var(--info)',
  },
  {
    title: 'Đơn hôm nay',
    value: '326',
    change: '+12.5%',
    up: true,
    color: 'var(--success)',
  },
  {
    title: 'Sắp hết hàng',
    value: '43',
    change: '-3.1%',
    up: false,
    color: 'var(--warning)',
  },
  {
    title: 'Lỗi kiểm kho',
    value: '7',
    change: '-1.4%',
    up: false,
    color: 'var(--danger)',
  },
]

const activities = [
  { time: '09:12', text: 'Phiếu nhập #PN-1021 đã được xác nhận' },
  { time: '10:05', text: 'Đơn xuất #PX-447 đang chờ đóng gói' },
  { time: '11:20', text: 'SKU SP-008 chạm ngưỡng tồn tối thiểu' },
  { time: '13:10', text: 'Hoàn tất kiểm kho khu vực B2' },
]
</script>

<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col v-for="card in kpiCards" :key="card.title" :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="content-card kpi-card">
          <p class="kpi-title">{{ card.title }}</p>
          <h2 class="kpi-value">{{ card.value }}</h2>
          <div class="kpi-change" :style="{ color: card.color }">
            <el-icon v-if="card.up"><ArrowUp /></el-icon>
            <el-icon v-else><ArrowDown /></el-icon>
            <span>{{ card.change }} so với hôm qua</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-16">
      <el-col :xs="24" :lg="16">
        <el-card class="content-card">
          <template #header>
            <div>
              <h3 class="page-title">Hiệu suất kho theo tuần</h3>
              <p class="page-subtitle">Mô phỏng xu hướng nhập/xuất để theo dõi nhanh</p>
            </div>
          </template>
          <div class="chart-placeholder">
            <div class="bar" style="height: 45%" />
            <div class="bar" style="height: 60%" />
            <div class="bar" style="height: 52%" />
            <div class="bar" style="height: 72%" />
            <div class="bar" style="height: 66%" />
            <div class="bar" style="height: 80%" />
            <div class="bar" style="height: 74%" />
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card class="content-card">
          <template #header>
            <h3 class="page-title">Hoạt động gần nhất</h3>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="item in activities"
              :key="item.time + item.text"
              :timestamp="item.time"
              placement="top"
            >
              {{ item.text }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.kpi-card {
  margin-bottom: 16px;
}

.kpi-title {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.kpi-value {
  margin: 10px 0;
  font-size: 30px;
}

.kpi-change {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
}

.mt-16 {
  margin-top: 0;
}

.chart-placeholder {
  height: 280px;
  border-radius: 10px;
  background: linear-gradient(180deg, #eff6ff, #ffffff);
  border: 1px dashed #cbd5e1;
  display: flex;
  align-items: flex-end;
  justify-content: space-evenly;
  padding: 18px;
}

.bar {
  width: 36px;
  border-radius: 8px 8px 0 0;
  background: linear-gradient(180deg, #60a5fa, #2563eb);
}
</style>