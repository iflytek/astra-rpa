<script lang="ts" setup>
import { computed } from 'vue'

import { useSharedData } from '@/stores/useSharedData'

defineOptions({
  name: 'AtomRemoteSelect',
})
const { renderData } = defineProps({
  renderData: {
    type: Object as () => any,
    default: () => ({}),
  },
})
const emit = defineEmits(['refresh'])
const shareDataStore = useSharedData()

const selectOptions = computed(() => {
  // renderData.options = shareDataStore.sharedVariables.map(i => i)
  return shareDataStore.sharedVariables
})
function handleChange(_value) {
  const data = selectOptions.value.find(i => i.value === _value)
  emit('refresh', data)
}

shareDataStore.getSharedVariables()
</script>

<template>
  <a-select
    v-model:value="renderData.value"
    class="bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.08)] text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)] rounded-[8px]"
    style="width: 100%;"
    @dropdown-visible-change="shareDataStore.getSharedVariables"
    @change="handleChange"
  >
    <a-select-option v-for="op in selectOptions" :key="op.value" :value="op.value" :label="op.label">
      {{ op.label }}
    </a-select-option>
  </a-select>
</template>
