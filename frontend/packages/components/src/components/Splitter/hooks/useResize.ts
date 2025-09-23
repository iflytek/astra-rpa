import { computed, ref } from 'vue'
import type { Ref } from 'vue'

import type { ItemType } from './useItems'
import type { ResizableInfo } from './useResizable'
import { getPtg } from './useSizes'

/**
 * Handle user drag resize logic.
 */
export default function useResize(
  items: Ref<ItemType[]>,
  resizableInfos: Ref<ResizableInfo[]>,
  percentSizes: Ref<number[]>,
  containerSize: Ref<number | undefined>,
  updateSizes: (sizes: number[]) => void,
  isRTL = false,
) {
  const limitSizes = computed(() => items.value.map(item => [item.min, item.max]))

  const mergedContainerSize = computed(() => containerSize.value || 0)
  const ptg2px = (ptg: number) => ptg * mergedContainerSize.value

  // ======================== Resize ========================
  function getLimitSize(
    str: string | number | undefined,
    defaultLimit: number,
  ) {
    if (typeof str === 'string') {
      return ptg2px(getPtg(str))
    }
    return str ?? defaultLimit
  }

  // Real px sizes
  const cacheSizes = ref<number[]>([])
  const cacheCollapsedSize: number[] = []

  /**
   * When start drag, check the direct is `start` or `end`.
   * This will handle when 2 splitter bar are in the same position.
   */
  const movingIndex = ref<{ index: number, confirmed: boolean } | null>(null)

  const getPxSizes = () => percentSizes.value.map(ptg2px)

  const onOffsetStart = (index: number) => {
    cacheSizes.value = getPxSizes()
    movingIndex.value = {
      index,
      confirmed: false,
    }
  }

  const onOffsetUpdate = (index: number, offset: number) => {
    // First time trigger move index update is not sync in the state
    let confirmedIndex: number | null = null

    // We need to know what the real index is.
    if ((!movingIndex.value || movingIndex.value.confirmed) && offset !== 0) {
      // Search for the real index
      if (offset > 0) {
        confirmedIndex = index
        movingIndex.value = {
          index,
          confirmed: true,
        }
      }
      else {
        for (let i = index; i >= 0; i -= 1) {
          if (cacheSizes.value[i] > 0 && resizableInfos.value[i].resizable) {
            confirmedIndex = i
            movingIndex.value = {
              index: i,
              confirmed: true,
            }
            break
          }
        }
      }
    }
    const mergedIndex = confirmedIndex ?? movingIndex.value?.index ?? index

    const numSizes = [...cacheSizes.value]
    const nextIndex = mergedIndex + 1

    // Get boundary
    const startMinSize = getLimitSize(limitSizes.value[mergedIndex][0], 0)
    const endMinSize = getLimitSize(limitSizes.value[nextIndex][0], 0)
    const startMaxSize = getLimitSize(
      limitSizes.value[mergedIndex][1],
      mergedContainerSize.value,
    )
    const endMaxSize = getLimitSize(
      limitSizes.value[nextIndex][1],
      mergedContainerSize.value,
    )

    let mergedOffset = offset

    // Align with the boundary
    if (numSizes[mergedIndex] + mergedOffset < startMinSize) {
      mergedOffset = startMinSize - numSizes[mergedIndex]
    }
    if (numSizes[nextIndex] - mergedOffset < endMinSize) {
      mergedOffset = numSizes[nextIndex] - endMinSize
    }
    if (numSizes[mergedIndex] + mergedOffset > startMaxSize) {
      mergedOffset = startMaxSize - numSizes[mergedIndex]
    }
    if (numSizes[nextIndex] - mergedOffset > endMaxSize) {
      mergedOffset = numSizes[nextIndex] - endMaxSize
    }

    // Do offset
    numSizes[mergedIndex] += mergedOffset
    numSizes[nextIndex] -= mergedOffset

    updateSizes(numSizes)

    return numSizes
  }

  const onOffsetEnd = () => {
    movingIndex.value = null
  }

  // ======================= Collapse =======================
  const onCollapse = (index: number, type: 'start' | 'end') => {
    const currentSizes = getPxSizes()
    const adjustedType = isRTL ? (type === 'start' ? 'end' : 'start') : type

    const currentIndex = adjustedType === 'start' ? index : index + 1
    const targetIndex = adjustedType === 'start' ? index + 1 : index

    const currentSize = currentSizes[currentIndex]
    const targetSize = currentSizes[targetIndex]

    if (currentSize !== 0 && targetSize !== 0) {
      // Collapse directly
      currentSizes[currentIndex] = 0
      currentSizes[targetIndex] += currentSize
      cacheCollapsedSize[index] = currentSize
    }
    else {
      const totalSize = currentSize + targetSize

      const currentSizeMin = getLimitSize(limitSizes.value[currentIndex][0], 0)
      const currentSizeMax = getLimitSize(
        limitSizes.value[currentIndex][1],
        mergedContainerSize.value,
      )
      const targetSizeMin = getLimitSize(limitSizes.value[targetIndex][0], 0)
      const targetSizeMax = getLimitSize(
        limitSizes.value[targetIndex][1],
        mergedContainerSize.value,
      )

      const limitStart = Math.max(currentSizeMin, totalSize - targetSizeMax)
      const limitEnd = Math.min(currentSizeMax, totalSize - targetSizeMin)
      const halfOffset = (limitEnd - limitStart) / 2

      const targetCacheCollapsedSize = cacheCollapsedSize[index]
      const currentCacheCollapsedSize = totalSize - targetCacheCollapsedSize

      const shouldUseCache
        = targetCacheCollapsedSize
          && targetCacheCollapsedSize <= targetSizeMax
          && targetCacheCollapsedSize >= targetSizeMin
          && currentCacheCollapsedSize <= currentSizeMax
          && currentCacheCollapsedSize >= currentSizeMin

      if (shouldUseCache) {
        currentSizes[targetIndex] = targetCacheCollapsedSize
        currentSizes[currentIndex] = currentCacheCollapsedSize
      }
      else {
        currentSizes[currentIndex] -= halfOffset
        currentSizes[targetIndex] += halfOffset
      }
    }

    updateSizes(currentSizes)

    return currentSizes
  }

  return [onOffsetStart, onOffsetUpdate, onOffsetEnd, onCollapse, movingIndex] as const
}
