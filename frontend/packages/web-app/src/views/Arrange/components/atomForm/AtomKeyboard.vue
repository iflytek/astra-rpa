<script setup lang="ts">
import { ref } from 'vue'

import ShortCutInput from '@/components/ShortcutInput/Index.vue'
import type { ShortcutItemMap } from '@/components/ShortcutInput/types'
import { OTHER_IN_TYPE } from '@/constants/atom'

const { renderData } = defineProps({
  renderData: {
    type: Object as () => RPA.AtomDisplayItem,
    default: () => ({}),
  },
})

const emits = defineEmits(['refresh'])

const keyObj = ref<ShortcutItemMap>({
  id: '',
  name: '',
  value: '',
  text: '点击设置按键',
})

const keyboardTextList = ref<string[]>([keyObj.value.text])

function initkeyboard() {
  const valueArr = renderData.value && Array.isArray(renderData.value) ? renderData.value : []
  const firstValue = (valueArr[0] || {}) as { value?: string }
  let value = ''
  let text = ''
  if (firstValue.value) {
    text = firstValue.value
    value = firstValue.value.replace(/\s*\+\s*/g, ',')
  }
  keyObj.value = {
    id: renderData.id || '',
    name: renderData.name || '',
    value,
    text: text || '点击设置按键',
  }
}

initkeyboard()

function handleChange(val) {
  const { text, value: keyVal } = val
  keyboardTextList.value = [text]
  if (keyVal) {
    renderData.value = [{ type: OTHER_IN_TYPE, value: text }]
  }
  else {
    renderData.value = []
  }
  emits('refresh')
}
</script>

<template>
  <ShortCutInput v-model="keyObj" :keyboard-text-list="keyboardTextList" @change="handleChange" />
</template>
