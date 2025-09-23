<!-- @format -->
<script setup lang="ts">
import { isEqual } from 'lodash-es'
import { onBeforeUnmount, watch } from 'vue'

import BUS from '@/utils/eventBus'

import { setInputPos, setTriggerPreId } from '@/views/Arrange/components/triggerInsert/hooks/useTriggerInput'
import TriggerInput from '@/views/Arrange/components/triggerInsert/TriggerInput.vue'

const { ids } = defineProps({
  ids: {
    type: Array<any>,
  },
})

const emits = defineEmits(['select'])

// 默认最后一个节点后展示输入框
function reset() {
  setTriggerPreId(ids[ids.length - 1] || '')
  setInputPos('bottom')
}

watch(() => ids, (val, oldVal) => {
  if (isEqual(val, oldVal))
    return
  reset()
}, {
  immediate: true,
})

function insert(key: string) {
  emits('select', key)
  reset()
}

BUS.$on('closeSearch', reset)

onBeforeUnmount(() => {
  setTriggerPreId('')
  setInputPos('')
  BUS.$off('closeSearch', reset)
})
</script>

<template>
  <div class="trigger-insert">
    <div class="trigger-insert-input">
      <TriggerInput v-if="ids.length === 0" @select="insert" />
    </div>
    <slot />
  </div>
</template>

<style scoped lang="scss">
.trigger-insert {
  height: 100%;
}
.trigger-insert-input {
  padding-left: 82px;
}
</style>
