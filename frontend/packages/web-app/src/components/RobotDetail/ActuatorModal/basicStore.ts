import { createInjectionState } from '@vueuse/core'
import { onBeforeMount, ref, shallowRef } from 'vue'

import { getRobotBasicInfo } from '@/api/robot'

interface BasicContentData {
  createTime: string
  creatorName: string
  fileName: string
  filePath: string
  introduction: string
  robotName: string
  sourceName: string
  useDescription: string
  versionNum: number
  versionInfoList: Array<{
    createTime: string
    online: number
    versionNum: number
  }>
}

const [useProvideBasicStore, useBasicStore] = createInjectionState((robotId: string) => {
  const loading = ref(false)
  const data = shallowRef<BasicContentData>(null)

  onBeforeMount(async () => {
    loading.value = true
    data.value = await getRobotBasicInfo(robotId)
    loading.value = false
  })

  return { loading, data }
})

export { useBasicStore, useProvideBasicStore }
