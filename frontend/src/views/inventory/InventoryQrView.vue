<template>
  <el-card class="content-card">
    <template #header>
      <div>
        <h2 class="page-title">QR Inventory</h2>
        <p class="page-subtitle">Lấy và hiển thị mã QR từ API inventory theo ID</p>
      </div>
    </template>

    <el-form label-width="120px" class="qr-form">
      <el-row :gutter="16">
        <el-col :xs="24" :md="10">
          <el-form-item label="Inventory ID">
            <el-input-number v-model="inventoryId" :min="1" style="width: 100%" />
          </el-form-item>
        </el-col>

        <el-col :xs="24" :md="14">
          <el-form-item label="Xem QR">
            <InventoryQrViewer :inventory-id="inventoryId" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import InventoryQrViewer from '@/components/InventoryQrViewer.vue'

const inventoryId = ref(1)
</script>

<style scoped>
.qr-form {
  max-width: 1000px;
}
</style>