import { computed } from 'vue'
import type { Ref } from 'vue'

import type { ItemType } from './useItems'

export interface ResizableInfo {
  resizable: boolean
  startCollapsible: boolean
  endCollapsible: boolean
}

export default function useResizable(items: Ref<ItemType[]>, pxSizes: Ref<number[]>, isRTL = false) {
  return computed(() => {
    const resizeInfos: ResizableInfo[] = []

    for (let i = 0; i < items.value.length - 1; i += 1) {
      const prevItem = items.value[i]
      const nextItem = items.value[i + 1]
      const prevSize = pxSizes.value[i]
      const nextSize = pxSizes.value[i + 1]

      const {
        resizable: prevResizable = true,
        min: prevMin,
        collapsible: prevCollapsible,
      } = prevItem
      const {
        resizable: nextResizable = true,
        min: nextMin,
        collapsible: nextCollapsible,
      } = nextItem

      const mergedResizable
        // Both need to be resizable
        = prevResizable
          && nextResizable
        // Prev is not collapsed and limit min size
          && (prevSize !== 0 || !prevMin)
        // Next is not collapsed and limit min size
          && (nextSize !== 0 || !nextMin)

      const startCollapsible
        // Self is collapsible
        = (prevCollapsible.end && prevSize > 0)
        // Collapsed and can be collapsed
          || (nextCollapsible.start && nextSize === 0 && prevSize > 0)

      const endCollapsible
        // Self is collapsible
        = (nextCollapsible.start && nextSize > 0)
        // Collapsed and can be collapsed
          || (prevCollapsible.end && prevSize === 0 && nextSize > 0)

      resizeInfos[i] = {
        resizable: mergedResizable,
        startCollapsible: !!(isRTL ? endCollapsible : startCollapsible),
        endCollapsible: !!(isRTL ? startCollapsible : endCollapsible),
      }
    }

    return resizeInfos
  })
}
