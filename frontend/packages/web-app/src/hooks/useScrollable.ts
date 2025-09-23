import { useResizeObserver } from '@vueuse/core'
import type { Ref } from 'vue'
import { ref } from 'vue'

export function useScrollable(el: Ref<HTMLElement | null>) {
  const isScrollable = ref(false)

  const check = () => {
    if (!el.value)
      return

    // 检测垂直滚动
    const canScrollY = el.value.scrollHeight > el.value.clientHeight
    // 检测水平滚动
    const canScrollX = el.value.scrollWidth > el.value.clientWidth

    // 获取实际应用的 CSS 属性
    const style = window.getComputedStyle(el.value)
    const overflowY = style.overflowY
    const overflowX = style.overflowX

    isScrollable.value
      = (canScrollY && (overflowY === 'auto' || overflowY === 'scroll'))
        || (canScrollX && (overflowX === 'auto' || overflowX === 'scroll'))
  }

  // 监听元素尺寸变化
  useResizeObserver(el, check)

  // 立即执行一次检测
  check()

  return isScrollable
}
