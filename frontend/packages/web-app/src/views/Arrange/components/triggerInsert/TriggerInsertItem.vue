<!-- @format -->
<script setup lang="ts">
import { inject, ref, watch } from 'vue'

import TriggerInput from '@/views/Arrange/components/triggerInsert/TriggerInput.vue'

const { id, index, indent } = defineProps({
  id: {
    type: String,
  },
  index: {
    type: Number,
  },
  indent: {
    type: Number,
  },
})

const emits = defineEmits(['select'])

const triggerId = inject('triggerId', ref(''))
const inputPos = inject('inputPos', ref(''))
const triggerIds = inject('triggerIds', ref([]))
const reset = inject('reset', () => {})

const addPos = ref('') // 添加按钮位置 top | bottom
const addPosStyle = ref({}) // 添加按钮样式

const preId = ref('') // 前置节点的id
const nextId = ref('') // 后置节点的id
const content = ref() // 节点内容

watch(() => triggerIds.value, (val) => {
  preId.value = val[index - 1] || ''
  nextId.value = val[index + 1] || ''
}, {
  immediate: true,
})

function canInsert(pos: string) {
  // 当前pos为top， 则前一个节点存在输入框，且pos为bottom，则不允许再次插入
  if (pos === 'top' && triggerId.value && preId.value && triggerId.value === preId.value && inputPos.value === 'bottom') {
    return false
  }
  // 当前pos为bottom， 则后一个节点的存在输入框，且pos为top，则不允许再次插入
  if (pos === 'bottom' && triggerId.value && nextId.value && triggerId.value === nextId.value && inputPos.value === 'top') {
    return false
  }
  // 当前的节点展示了输入框，且输入框的位置和计算位置相同，则输入框的位置不允许再次插入
  if (triggerId.value === id && pos === inputPos.value) {
    return false
  }
  return true
}

function mouseMove(e: MouseEvent) {
  if (content.value) {
    const domRect = content.value.getBoundingClientRect()
    const pos = e.clientY > domRect.top + domRect.height / 2 ? 'bottom' : 'top'
    if (canInsert(pos)) {
      addPosStyle.value = {
        top: pos === 'top' ? `${domRect.top - 13}px` : `${domRect.bottom - 13}px`,
      }
      addPos.value = pos
    }
    else {
      addPosStyle.value = {}
      addPos.value = ''
    }
  }
}

function mouseLeave() {
  addPosStyle.value = {}
  addPos.value = ''
}

// 展示输入框
function showTriggerInput() {
  triggerId.value = id
  inputPos.value = addPos.value
  addPosStyle.value = {}
  addPos.value = ''
}

function clickAtom(key: string) {
  const addToIndex = inputPos.value === 'top' ? index : index + 1
  emits('select', key, addToIndex)
  reset()
}
</script>

<template>
  <div
    ref="content" class="trigger-insert-item relative"
    :data-id="id"
    :data-indent="indent"
    @mousemove="mouseMove"
    @mouseleave="mouseLeave"
  >
    <div ref="addAtomBtn" class="addAtom" :class="addPos" :style="addPosStyle">
      <span class="addAtom-btn" @click="showTriggerInput">+</span>
      <span class="addAtom-line" />
    </div>
    <div v-if="triggerId === id && inputPos === 'top'" class="trigger-insert-item-input">
      <TriggerInput @select="clickAtom" />
    </div>
    <slot />
    <div v-if="triggerId === id && inputPos === 'bottom'" class="trigger-insert-item-input">
      <TriggerInput @select="clickAtom" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.trigger-insert-item {
  &-input {
    padding-left: 82px;
  }
}
.addAtom {
  position: fixed;
  left: 325px;
  z-index: 1000;
  width: calc(100% - 70px);
  height: 20px;
  text-align: left;
  display: none;
  &.bottom,
  &.top {
    display: block;
  }

  &-btn {
    display: inline-block;
    width: 24px;
    height: 24px;
    line-height: 24px;
    border-radius: 20px;
    color: #fff;
    font-size: 14px;
    cursor: pointer;
    text-align: center;
    background: $color-primary;

    &:hover {
      & + .addAtom-line {
        display: block;
      }
    }
  }

  &-line {
    width: calc(100% - 5px);
    margin-left: 0px;
    height: 1px;
    border-bottom: 2px dashed rgba(72, 106, 255, 0.41);
    display: none;
    margin-top: -12px;
  }
}
</style>
