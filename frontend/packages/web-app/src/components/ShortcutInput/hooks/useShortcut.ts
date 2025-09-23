import { onBeforeUnmount, ref } from 'vue'

import { getKeyboard, resetKeyboard } from '@/utils/hotkeys'

import type { ShortcutItemMap } from '@/components/ShortcutInput/types.ts'

export function useShortcut(modelValue: ShortcutItemMap, emit) {
  const inputItem = ref(modelValue)

  const setInputItem = (data) => {
    inputItem.value = {
      ...inputItem.value,
      ...data,
    }
    emit('update:modelValue', inputItem.value)
    emit('change', inputItem.value)
    if (typeof (data.active) === 'boolean') {
      data.active ? emit('focus', inputItem.value) : emit('blur', inputItem.value)
    }
  }

  // 等待键盘输入
  const waitKeyboard = (e: Event) => {
    e.stopPropagation()
    const obj: any = { active: true }
    if (inputItem.value.text === '点击设置按键') {
      obj.text = '输入按键'
    }
    setInputItem(obj)

    getKeyboard(inputItem.value, ({ text, value }) => {
      setInputItem({
        text,
        value,
      })
    })
  }

  // 关闭快捷键输入
  const closeWaitKeyboard = (e: Event) => {
    e.stopPropagation()
    setInputItem({
      text: '点击设置按键',
      active: false,
    })
    resetKeyboard()
  }

  // 已设置快捷键，关闭
  const closeActiveKeyboard = (e: Event) => {
    e.stopPropagation()
    setInputItem({
      text: '输入新的按键',
      value: '',
      active: true,
    })
    getKeyboard(inputItem.value, ({ text, value }) => {
      setInputItem({
        text,
        value,
      })
    })
  }

  onBeforeUnmount(() => {
    resetKeyboard()
  })

  return {
    waitKeyboard,
    closeWaitKeyboard,
    closeActiveKeyboard,
    inputItem,
    setInputItem,
    resetKeyboard,
  }
}
