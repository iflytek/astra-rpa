import { createInjectionState } from '@vueuse/core'
import type { MaybeRef } from 'vue'
import { computed, ref, unref, watch } from 'vue'

type Position = 'top' | 'bottom' | ''

const [useRenderListProvide, useRenderList] = createInjectionState((rawList: MaybeRef<RPA.Atom[]>) => {
  const renderList = computed(() => [...unref(rawList).slice(0, insertItemIndex.value), unref(insertItem), ...unref(rawList).slice(insertItemIndex.value)]) // 包含额外插入项的待渲染列表
  const insertItem = ref({ id: 'insertItem' } as RPA.Atom) // 额外插入项
  const insertItemIndex = ref(unref(rawList).length) // 额外插入项索引
  const insertItemLast = computed(() => renderList.value[insertItemIndex.value - 1]) // 插入项上一列表项
  const insertItemNext = computed(() => renderList.value[insertItemIndex.value + 1]) // 插入项下一列表项

  function triggerInsert(item: RPA.Atom, position: Position) {
    const index = adjustIndex(renderList.value.findIndex(i => i.id === item.id)) // 获取触发项索引（校正后）
    const targetIndex = position === 'top' ? index : index + 1 // 若触发位置为bottom，目标插入索引需加一
    insertItemIndex.value = targetIndex
  }

  function resetRenderList() {
    insertItemIndex.value = unref(rawList).length
  }

  function adjustIndex(index: number, isInsert?: boolean) {
    if (isInsert) {
      return index > insertItemIndex.value ? Math.max(index - 1, 0) : index
    }
    else {
      return index >= insertItemIndex.value ? Math.max(index - 1, 0) : index
    }
  }

  function canInsert(item: RPA.Atom, position: Position) {
    if (item.id === insertItem.value.id) {
      return false
    }
    else if (position === 'top' && item.id === insertItemNext.value?.id) {
      return false
    }
    else if (position === 'bottom' && item.id === insertItemLast.value?.id) {
      return false
    }
    else {
      return true
    }
  }

  watch(() => unref(rawList).length, (newVal, oldVal) => {
    // 新增/删除节点时重置插入项位置
    if (newVal !== oldVal) {
      resetRenderList()
    }
  })

  return {
    renderList,
    insertItem,
    insertItemIndex,
    insertItemLast,
    insertItemNext,
    triggerInsert,
    canInsert,
    adjustIndex,
    resetRenderList,
  }
})

export { useRenderList, useRenderListProvide }
