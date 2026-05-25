<script setup lang="ts">
import {
  DataAnalysis,
  Goods,
  Histogram,
  Operation,
  PictureFilled,
  SwitchButton,
  Van,
} from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

type MenuItem = {
  index: string
  label: string
  icon: any
}

const route = useRoute()
const router = useRouter()

const menuItems: MenuItem[] = [
  { index: '/dashboard', label: 'Dashboard', icon: DataAnalysis },
  { index: '/products', label: 'Sản phẩm', icon: Goods },
  { index: '/inventory', label: 'Tồn kho', icon: Histogram },
  { index: '/inventory-qr', label: 'QR Inventory', icon: PictureFilled },
  { index: '/inbound-outbound', label: 'Nhập / Xuất kho', icon: Van },
  { index: '/reports', label: 'Báo cáo', icon: Operation },
]

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const found = menuItems.find((item) => item.index === route.path)
  return found?.label ?? 'Warehouse'
})

const now = computed(() =>
  new Date().toLocaleString('vi-VN', {
    weekday: 'short',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }),
)

function handleMenuSelect(index: string) {
  router.push(index)
}
</script>

<template>
  <el-container class="main-layout">
    <el-aside width="250px" class="sidebar">
      <div class="brand">
        <el-icon :size="26"><Goods /></el-icon>
        <div>
          <h2>Warehouse Admin</h2>
          <p>Inventory Management</p>
        </div>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="transparent"
        text-color="var(--text-light)"
        active-text-color="#ffffff"
        @select="handleMenuSelect"
      >
        <el-menu-item v-for="item in menuItems" :key="item.index" :index="item.index">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div>
          <h1>{{ pageTitle }}</h1>
          <p>Dữ liệu cập nhật theo thời gian thực cho hoạt động kho</p>
        </div>
        <div class="topbar-right">
          <el-tag type="info" effect="plain">{{ now }}</el-tag>
          <el-avatar :size="36">AD</el-avatar>
          <el-button type="danger" plain :icon="SwitchButton">Đăng xuất</el-button>
        </div>
      </el-header>

      <el-main class="page-content">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.main-layout {
  min-height: 100vh;
}

.sidebar {
  background: var(--bg-sidebar);
  color: var(--text-light);
  border-right: 1px solid #334155;
  padding: 16px 12px;
}

.brand {
  display: flex;
  gap: 10px;
  align-items: center;
  color: #fff;
  padding: 6px 10px 16px;
  border-bottom: 1px solid #334155;
  margin-bottom: 14px;
}

.brand h2 {
  margin: 0;
  font-size: 18px;
}

.brand p {
  margin: 2px 0 0;
  font-size: 12px;
  color: #9ca3af;
}

.sidebar-menu {
  border-right: none;
}

:deep(.sidebar-menu .el-menu-item) {
  border-radius: 10px;
  margin-bottom: 6px;
}

:deep(.sidebar-menu .el-menu-item.is-active) {
  background: var(--bg-sidebar-active);
  font-weight: 600;
}

.topbar {
  height: auto;
  min-height: 70px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
}

.topbar h1 {
  margin: 0;
  font-size: 20px;
}

.topbar p {
  margin: 4px 0 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-content {
  padding: 20px;
}
</style>