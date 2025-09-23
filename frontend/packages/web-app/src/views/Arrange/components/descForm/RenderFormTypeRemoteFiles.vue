<script setup lang="ts">
import { computed } from 'vue'

import { replaceMiddle } from '@/utils/common'

import { useSharedData } from '@/stores/useSharedData'

const { itemData } = defineProps({
  itemData: {
    type: Object as any,
    default: () => ({}),
  },
})
const sharedData = useSharedData()
const fileName = computed(() => {
  return sharedData.sharedFiles.find(i => i.fileId === itemData.value[0]?.value)?.fileName || ''
})
</script>

<template>
  <a-tooltip placement="top" :title="fileName">
    <span class="desc-btn inline-flex items-center text-[#2FCB64]/[.9]">
      {{ replaceMiddle(fileName) }}
    </span>
  </a-tooltip>
</template>
