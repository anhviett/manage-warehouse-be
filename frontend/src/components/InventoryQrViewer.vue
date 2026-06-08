<template>
  <div class="inventory-qr-viewer">
    <div class="inventory-qr-viewer__toolbar">
      <el-text tag="b">QR Inventory #{{ inventoryId }}</el-text>
      <el-button type="primary" plain size="small" :loading="loading" @click="fetchQr">
        Tải QR
      </el-button>
    </div>

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="inventory-qr-viewer__alert"
    />

    <el-skeleton v-if="loading" :rows="4" animated />

    <div v-else class="inventory-qr-viewer__content">
      <el-empty
        v-if="!qrImageSrc && !qrLabel && !qrPayloadText"
        description="Chưa có dữ liệu QR"
      />

      <div v-else class="inventory-qr-viewer__result">
        <img
          v-if="qrImageSrc"
          :src="qrImageSrc"
          alt="Inventory QR"
          class="inventory-qr-viewer__image"
        />

        <el-input
          v-if="qrLabel"
          :model-value="qrLabel"
          readonly
        />

        <el-input
          v-if="qrPayloadText"
          :model-value="qrPayloadText"
          type="textarea"
          :rows="10"
          readonly
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { getInventoryQr, type InventoryQrResponse } from '@/services/inventories'

const props = defineProps<{
  inventoryId: number | string
  autoFetch?: boolean
}>()

const loading = ref(false)
const error = ref('')
const qrResponse = ref<InventoryQrResponse | null>(null)

const qrImageSrc = computed(() => {
  const imageBase64 = qrResponse.value?.image_base64
  return imageBase64 ? `data:image/png;base64,${imageBase64}` : ''
})

const qrLabel = computed(() => qrResponse.value?.label ?? '')

const qrPayloadText = computed(() => {
  const payload = qrResponse.value?.payload
  return payload ? JSON.stringify(payload, null, 2) : ''
})

async function fetchQr() {
  loading.value = true
  error.value = ''

  try {
    qrResponse.value = await getInventoryQr(props.inventoryId)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Không thể tải QR inventory'
    qrResponse.value = null
  } finally {
    loading.value = false
  }
}

watch(
  () => props.inventoryId,
  async (newId) => {
    if (props.autoFetch !== false && newId !== '' && newId !== undefined && newId !== null) {
      await fetchQr()
    }
  },
)

onMounted(async () => {
  if (props.autoFetch !== false && props.inventoryId !== '' && props.inventoryId !== undefined && props.inventoryId !== null) {
    await fetchQr()
  }
})
</script>

<style scoped>
.inventory-qr-viewer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.inventory-qr-viewer__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.inventory-qr-viewer__alert {
  margin-bottom: 4px;
}

.inventory-qr-viewer__content {
  min-height: 120px;
}

.inventory-qr-viewer__result {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.inventory-qr-viewer__image {
  width: 240px;
  max-width: 100%;
  border: 1px solid var(--el-border-color);
  border-radius: 12px;
  padding: 12px;
  background: #fff;
}
</style>