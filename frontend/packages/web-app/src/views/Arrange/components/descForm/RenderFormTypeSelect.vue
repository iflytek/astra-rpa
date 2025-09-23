<script setup lang="ts">
import type { Ref } from 'vue'
import { computed, inject } from 'vue'

import { useFlowStore } from '@/stores/useFlowStore'
import { isConditionalKeys } from '@/views/Arrange/components/atomForm/hooks/useBaseConfig'

const { itemData, desc, id, canEdit } = defineProps({
  desc: {
    type: String,
    default: '',
  },
  itemData: {
    type: Object as () => RPA.AtomDisplayItem,
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
const isEmpty = computed(() => menuItems().length === 0)

function click(val: string) {
  itemData.value = val
  useFlowStore().setFormItemValue(itemData.key, itemData.value, id)
  if (isConditionalKeys(itemData.key))
    isShowFormItem.value = !isShowFormItem.value
}

function menuItems() {
  return itemData.options?.map(i => ({ key: i.value, label: i.label })) ?? []
}
</script>

<template>
  <!-- 下拉选择、单选、切换、复选框 -->
  <a-dropdown :disabled="!canEdit || isEmpty">
    <span>{{ isEmpty ? '--' : desc }}</span>
    <template #overlay>
      <a-menu mode="vertical" :items="menuItems()" @click="(item) => click(item.key as string)" />
    </template>
  </a-dropdown>
</template>
