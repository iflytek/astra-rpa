<script setup lang="ts">
import type { Ref } from 'vue'
import { computed, inject } from 'vue'

import { useFlowStore } from '@/stores/useFlowStore'
import { useSharedData } from '@/stores/useSharedData'
import { isConditionalKeys } from '@/views/Arrange/components/atomForm/hooks/useBaseConfig'

const { itemData, id, canEdit } = defineProps({
  itemData: {
    type: Object as any,
    default: () => ({}),
  },
  id: {
    type: String,
    default: '',
  },
  canEdit: {
    type: Boolean,
    default: true,
  },
})
const isShowFormItem = inject<Ref<boolean>>('showAtomFormItem')

const sharedData = useSharedData()

function click({ item }) {
  itemData.value = item.originItemValue.key
  useFlowStore().setFormItemValue(itemData.key, itemData.value, id)
  if (isConditionalKeys(itemData.key))
    isShowFormItem.value = !isShowFormItem.value
}

const menuItems = computed(() => {
  // itemData.options = sharedData.sharedVariables.map(i => i)
  return sharedData.sharedVariables.map(i => ({
    key: i.value,
    label: i.label,
  })) ?? []
})

const itemLabel = computed(() => {
  return sharedData.sharedVariables.find(i => i.value === itemData.value)?.label || ''
})

function openChange(open) {
  if (open) {
    sharedData.getSharedVariables()
  }
}
</script>

<template>
  <!-- 下拉选择、单选、切换、复选框 -->
  <a-dropdown :disabled="!canEdit" @open-change="openChange">
    <span>{{ itemLabel }}</span>
    <template #overlay>
      <a-menu mode="vertical" :items="menuItems" class="h-60 overflow-y-auto" @click="(item) => click(item)" />
    </template>
  </a-dropdown>
</template>
