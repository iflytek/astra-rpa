<script setup lang="ts">
import { CheckOutlined, CloseOutlined } from '@ant-design/icons-vue'
import { computed, ref, watch } from 'vue'

import { useShortcut } from '@/components/ShortcutInput/hooks/useShortcut'
import type { ShortcutItemMap } from '@/components/ShortcutInput/types.ts'

const { modelValue, keyboardTextList, cssModel } = defineProps({
  modelValue: {
    type: Object as () => ShortcutItemMap,
    required: true,
  },
  keyboardTextList: {
    type: Array as () => string[],
    default: () => ['点击设置按键'],
  },
  cssModel: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'change', 'focus', 'blur'])
const { inputItem, waitKeyboard, closeWaitKeyboard, closeActiveKeyboard, setInputItem, resetKeyboard } = useShortcut(modelValue, emit)

watch(() => modelValue, (val, oldVal) => {
  if (val.validate !== oldVal?.validate || val.value !== oldVal?.value) {
    setInputItem(val)
  }
})

const bgStyle = computed(() => {
  const borderDefault = 'border:none;'
  const borderActive = 'border:1px solid #40a9ff;box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);'
  return (inputItem.value.active && !['输入按键', '输入新的按键'].includes(inputItem.value.text)
    ? borderActive
    : borderDefault)
  + cssModel
})

const showClose = computed(() => {
  return keyboardTextList.includes(inputItem.value.text)
})

const showSuccess = ref(false)

function handleClose(e: Event) {
  ['输入按键', '输入新的按键'].includes(inputItem.value.text)
    ? closeWaitKeyboard(e)
    : closeActiveKeyboard(e)
  showSuccess.value = false
}
function handleInput(e: Event) {
  showSuccess.value = true
  waitKeyboard(e)
}
function handleOk() {
  resetKeyboard()
  showSuccess.value = false
}
</script>

<template>
  <div class="shortCutInput w-full">
    <div
      :style="bgStyle"
      class="w-full max-w-[320px] h-[32px] leading-[22px] text-[rgba(0,0,0,0.85)] dark:text-[rgba(255,255,255,0.85)] py-[5px] px-[11px] rounded-[6px] relative outline-none bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.08)]"
      tabindex="0"
      @click="handleInput"
      @blur="handleOk"
    >
      <span class="font-semibold">
        {{ inputItem.text }}
      </span>
      <CloseOutlined
        v-if="showClose"
        class="cursor-pointer float-right pt-1 pl-2"
        @click="handleClose"
      />
      <CheckOutlined v-if="showSuccess" class="cursor-pointer float-right pt-1" @click.stop="handleOk" />
      <span class="shortCutInput-validate">
        {{ inputItem.validate }}
      </span>
    </div>
  </div>
</template>

<style lang="scss">
.shortCutInput {
  height: 40px;
  display: flex;
  font-size: 12px;
  &-validate {
    color: red;
    position: absolute;
    left: 0;
    bottom: -18px;
    font-size: 12px;
    height: 12px;
    line-height: 12px;
  }
}
</style>
