<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useWareHouseProduct } from '@/composables/ware-house-product.composable'
import ProductView from '@/views/products/ProductView.vue'

const dialogProductCreate = ref(false);
const dialogProductView = ref(false);
const { products, loading, error, fetchWareHouseProducts, fetchWareHouseProductById } = useWareHouseProduct()

const searchText = ref('')

onMounted(() => {
  fetchWareHouseProducts()
})

const filteredProducts = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()

  if (!keyword) {
    return products.value
  }

  return products.value.filter((product) => {
    return [product.sku, product.name, product.category_name, product.supplier_name]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(keyword))
  })
})

const statusTagType = (isActive: boolean) => (isActive ? 'success' : 'info')

const formatPrice = (value?: number | string) => {
  const numericValue = Number(value ?? 0)
  return numericValue.toLocaleString('vi-VN')
}

const formatDateTime = (value?: string) => {
  if (!value) return '-'
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString('vi-VN')
}

const detailProduct = async (productId: number) => {
  await fetchWareHouseProductById(productId)
  // placeholder detail handler
  // implement navigation or dialog open as needed
  console.log('view details for product:', productId)
}
const editProduct = async (productId: number) => {
  // placeholder detail handler
  // implement navigation or dialog open as needed
  console.log('view details for product:', productId)
}
</script>

<template>
  <el-card class="content-card">
    <template #header>
      <div>
        <h2 class="page-title">Danh mục sản phẩm</h2>
        <p class="page-subtitle">Quản lý nhanh SKU, nhóm hàng và giá bán nội bộ</p>
      </div>
    </template>

    <el-row :gutter="12" class="toolbar">
      <el-col :xs="24" :md="10">
        <el-input v-model="searchText" placeholder="Tìm theo tên SKU/sản phẩm..." clearable />
      </el-col>
      <el-col :xs="24" :md="8">
        <el-select placeholder="Lọc theo nhóm hàng" style="width: 100%">
          <el-option label="Tất cả" value="all" />
          <el-option label="Thiết bị" value="device" />
          <el-option label="Lưu trữ" value="storage" />
          <el-option label="Vật tư" value="material" />
        </el-select>
      </el-col>
      <el-col :xs="24" :md="6" class="toolbar-right">
        <el-button type="primary">+ Thêm sản phẩm</el-button>
      </el-col>
    </el-row>

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="mb-16"
    />

    <el-table :data="filteredProducts" stripe v-loading="loading">
      <el-table-column prop="sku" label="SKU" width="120" />
      <el-table-column prop="name" label="Tên sản phẩm" min-width="260" />
      <el-table-column prop="category_name" label="Nhóm hàng" width="160" />
      <el-table-column prop="supplier_name" label="Nhà cung cấp" min-width="180" />
      <el-table-column prop="unit" label="Đơn vị" width="100" />
      <el-table-column label="Giá bán" width="150">
        <template #default="{ row }">{{ formatPrice(row.selling_price) }} đ</template>
      </el-table-column>
      <el-table-column label="Trạng thái" width="120">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.is_active)" effect="light">
            {{ row.is_active ? 'Đang hoạt động' : 'Ngừng hoạt động' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Tạo lúc" width="180">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="Thao tác" width="170">
        <template #default = "{ row }">
          <el-button size="small" text type="primary" @click="detailProduct(row.id)">Chi tiết</el-button>
          <el-button size="small" text type="warning" @click="editProduct(row.id)">Sửa</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
  <ProductCreate v-model:dialogProductCreate="dialogProductCreate" />
  <ProductView v-model:dialogProductView="dialogProductView" />
</template>

<style scoped>
.toolbar {
  margin-bottom: 14px;
}
.toolbar-right {
  display: flex;
  justify-content: flex-end;
}

.mb-16 {
  margin-bottom: 16px;
}
</style>