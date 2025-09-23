import { useDark, useResizeObserver } from '@vueuse/core'
import { computed, defineComponent, Fragment, h, ref, useTemplateRef } from 'vue'
import type { VNode } from 'vue'

import useItems from './hooks/useItems'
import useResizable from './hooks/useResizable'
import useResize from './hooks/useResize'
import useSizes from './hooks/useSizes'
import { splitterProps } from './interface'
import type { PanelProps } from './interface'
import { SplitBar } from './SplitBar'

export const Splitter = defineComponent({
  name: 'Splitter',
  props: splitterProps(),
  setup(props) {
    const isDark = useDark()
    const containerSize = ref<number | undefined>()
    const container = useTemplateRef<HTMLElement>('container')
    const items = useItems()

    const prefixCls = props.prefixCls || 'splitter'
    const maskCls = `${prefixCls}-mask`
    const isVertical = props.layout === 'vertical'
    const isRTL = false
    const reverse = !isVertical && isRTL

    const [
      panelSizes,
      itemPxSizes,
      itemPtgSizes,
      itemPtgMinSizes,
      itemPtgMaxSizes,
      updateSizes,
    ] = useSizes(items, containerSize)
    const resizableInfos = useResizable(items, itemPxSizes)
    const [
      onOffsetStart,
      onOffsetUpdate,
      onOffsetEnd,
      onCollapse,
      movingIndex,
    ] = useResize(items, resizableInfos, itemPtgSizes, containerSize, updateSizes)

    useResizeObserver(container, (entries) => {
      const entry = entries[0]
      const { width, height } = entry.contentRect
      const localContainerSize = isVertical ? height : width

      if (localContainerSize > 0) {
        containerSize.value = localContainerSize
      }
    })

    const stackSizes = computed(() => {
      const mergedSizes: number[] = []

      let stack = 0
      for (let i = 0; i < items.value.length; i += 1) {
        stack += itemPtgSizes.value[i]
        mergedSizes.push(stack)
      }

      return mergedSizes
    })

    // ======================== Events ========================
    function onInternalResizeStart(index: number) {
      onOffsetStart(index)
      props.onResizeStart?.(itemPxSizes.value)
    }

    function onInternalResizeUpdate(index: number, offsetX: number, offsetY: number) {
      let offset = isVertical ? offsetY : offsetX
      if (reverse) {
        offset = -offset
      }
      const nextSizes = onOffsetUpdate(index, offset)
      props.onResize?.(nextSizes)
    }

    function onInternalResizeEnd() {
      onOffsetEnd()
      props.onResizeEnd?.(itemPxSizes.value)
    }

    function onInternalCollapse(index: number, type: 'start' | 'end') {
      const nextSizes = onCollapse(index, type)
      props.onResize?.(nextSizes)
      props.onResizeEnd?.(nextSizes)
    }

    return () => (
      <div ref="container" class={[prefixCls, `${prefixCls}-${props.layout}`, { dark: isDark.value }]}>
        {items.value.map(({ node, ...item }, idx) => {
          // Panel
          const panel = h<PanelProps>(node, { ...item, prefixCls, size: panelSizes.value[idx] })

          // Split Bar
          let splitBar: VNode | null = null

          const resizableInfo = resizableInfos.value[idx]
          if (resizableInfo) {
            const ariaMinStart
              = (stackSizes.value[idx - 1] || 0) + itemPtgMinSizes.value[idx]
            const ariaMinEnd
              = (stackSizes.value[idx + 1] || 100) - itemPtgMaxSizes.value[idx + 1]

            const ariaMaxStart
              = (stackSizes.value[idx - 1] || 0) + itemPtgMaxSizes.value[idx]
            const ariaMaxEnd
              = (stackSizes.value[idx + 1] || 100) - itemPtgMinSizes.value[idx + 1]

            splitBar = (
              <SplitBar
                lazy={props.lazy}
                index={idx}
                active={movingIndex.value?.index === idx}
                prefixCls={prefixCls}
                vertical={isVertical}
                resizable={resizableInfo.resizable}
                ariaNow={stackSizes.value[idx] * 100}
                ariaMin={Math.max(ariaMinStart, ariaMinEnd) * 100}
                ariaMax={Math.min(ariaMaxStart, ariaMaxEnd) * 100}
                startCollapsible={resizableInfo.startCollapsible}
                endCollapsible={resizableInfo.endCollapsible}
                onOffsetStart={onInternalResizeStart}
                onOffsetUpdate={onInternalResizeUpdate}
                onOffsetEnd={onInternalResizeEnd}
                onCollapse={onInternalCollapse}
                containerSize={containerSize.value || 0}
              />
            )
          }

          return (
            // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
            <Fragment key={`split-panel-${idx}`}>
              {panel}
              {splitBar}
            </Fragment>
          )
        })}

        {/* Fake mask for cursor */}
        {typeof movingIndex === 'number' && (
          <div aria-hidden class={[maskCls, `${maskCls}-${props.layout}`]} />
        )}
      </div>
    )
  },
})
