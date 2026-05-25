import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        {
          path: '',
          redirect: '/dashboard',
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
        },
        {
          path: 'products',
          name: 'products',
          component: () => import('@/views/products/ProductsList.vue'),
        },
        {
          path: 'inventory',
          name: 'inventory',
          component: () => import('@/views/inventory/InventoryView.vue'),
        },
        {
          path: 'inventory-qr',
          name: 'inventory-qr',
          component: () => import('@/views/inventory/InventoryQrView.vue'),
        },
        {
          path: 'inbound-outbound',
          name: 'inbound-outbound',
          component: () => import('@/views/inbound-outbound/InboundOutboundView.vue'),
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('@/views/reports/ReportsView.vue'),
        },
      ],
    },
  ],
})

export default router