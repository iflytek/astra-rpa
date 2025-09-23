import { computed, ref } from 'vue'
import type { Ref } from 'vue'

import type { PanelProps } from '../interface'

export function getPtg(str: string) {
  return Number(str.slice(0, -1)) / 100
}

/**
 * 判断是否是文字 '百分比%' 类型
 * @param itemSize
 * @returns
 */
function isPtg(itemSize: string | number | undefined): itemSize is string {
  return typeof itemSize === 'string' && itemSize.endsWith('%')
}

/**
 * Save the size state.
 * Align the size into flex percentage base.
 */
export default function useSizes(items: Ref<PanelProps[]>, containerSize: Ref<number | undefined>) {
  const mergedContainerSize = computed(() => containerSize.value || 0)
  const ptg2px = (ptg: number) => ptg * mergedContainerSize.value

  // We do not need care the size state match the `items` length in `useState`.
  // It will calculate later.
  const innerSizes = ref<(string | number | undefined)[]>(
    items.value.map(item => item.defaultSize),
  )

  const sizes = computed(() => {
    const propSizes = items.value.map(item => item.size)
    const mergedSizes: PanelProps['size'][] = []

    for (let i = 0; i < items.value.length; i += 1) {
      mergedSizes[i] = propSizes[i] ?? innerSizes.value[i]
    }

    return mergedSizes
  })

  // 后续处理尺寸。具体操作如下：
  // 1. 将所有的 px 转换为百分比，如果不为空。
  // 2. 获取存在百分比的剩余百分比。
  // 3. 将剩余百分比填充到空项。
  const postPercentSizes = computed(() => {
    let ptgList: (number | undefined)[] = []
    let emptyCount = 0

    // Fill default percentage
    for (let i = 0; i < items.value.length; i += 1) {
      const itemSize = sizes.value[i]

      if (isPtg(itemSize)) {
        ptgList[i] = getPtg(itemSize)
      }
      else if (itemSize || itemSize === 0) {
        const num = Number(itemSize)
        if (!Number.isNaN(num)) {
          ptgList[i] = num / mergedContainerSize.value
        }
      }
      else {
        emptyCount += 1
        ptgList[i] = undefined
      }
    }

    const totalPtg = ptgList.reduce<number>((acc, ptg) => acc + (ptg || 0), 0)

    if (totalPtg > 1 || !emptyCount) {
      // If total percentage is larger than 1, we will scale it down.
      const scale = 1 / totalPtg
      ptgList = ptgList.map(ptg => (ptg === undefined ? 0 : ptg * scale))
    }
    else {
      // If total percentage is smaller than 1, we will fill the rest.
      const avgRest = (1 - totalPtg) / emptyCount
      ptgList = ptgList.map(ptg => (ptg === undefined ? avgRest : ptg))
    }

    return ptgList as number[]
  })

  const postPxSizes = computed(() => postPercentSizes.value.map(ptg2px))

  const postPercentMinSizes = computed(() =>
    items.value.map((item) => {
      if (isPtg(item.min)) {
        return getPtg(item.min)
      }
      return (item.min || 0) / mergedContainerSize.value
    }),
  )

  const postPercentMaxSizes = computed(() =>
    items.value.map((item) => {
      if (isPtg(item.max)) {
        return getPtg(item.max)
      }
      return (item.max || mergedContainerSize.value) / mergedContainerSize.value
    }),
  )

  // If ssr, we will use the size from developer config first.
  const panelSizes = computed(() => (containerSize.value ? postPxSizes.value : sizes.value))

  const setInnerSizes = (sizes: (string | number | undefined)[]) => {
    innerSizes.value = sizes
  }

  return [
    panelSizes,
    postPxSizes,
    postPercentSizes,
    postPercentMinSizes,
    postPercentMaxSizes,
    setInnerSizes,
  ] as const
}
