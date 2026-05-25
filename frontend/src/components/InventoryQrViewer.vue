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
        v-if="!qrImageSrc && !qrText"
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
          v-if="qrText"
          :model-value="qrText"
          type="textarea"
          :rows="4"
          readonly
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { getInventoryQr } from '@/services/inventories'

const props = defineProps<{
  inventoryId: number | string
  autoFetch?: boolean
}>()

const loading = ref(false)
const error = ref('')
const qrResponse = ref<Record<string, unknown> | null>(null)

const qrImageSrc = computed(() => {
  const candidates = [
    qrResponse.value?.qr_image,
    qrResponse.value?.qr_url,
    qrResponse.value?.image,
  ]

  const imageValue = candidates.find((value) => typeof value === 'string' && value.length > 0)
  return typeof imageValue === 'string' ? imageValue : ''
})

const qrText = computed(() => {
  const candidates = [
    qrResponse.value?.qr_code,
    qrResponse.value?.data,
  ]

  const textValue = candidates.find((value) => typeof value === 'string' && value.length > 0)
  return typeof textValue === 'string' ? textValue : ''
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