import { message } from 'ant-design-vue'
import { nextTick, watch } from 'vue'

import $loading from '@/utils/globalLoading'

import { useFlowStore } from '@/stores/useFlowStore'
import { useRunningStore } from '@/stores/useRunningStore'
import { atomScrollIntoView } from '@/views/Arrange/utils'

export function useRunDebug() {
  const runningStore = useRunningStore()
  // 每次debugData变化，自动滚动到当前debug的节点
  watch(() => runningStore?.breakpointAtom?.id, () => {
    const debugAtom = runningStore?.breakpointAtom
    if (debugAtom) {
      useFlowStore().setActiveAtom(useFlowStore().simpleFlowUIData.find(item => item.id === debugAtom.id))
      nextTick(() => atomScrollIntoView(debugAtom.id))
    }
  })

  // 监听运行调试状态，
  watch(() => runningStore?.status, () => {
    switch (runningStore?.status) {
      case 'starting':
        $loading.open({ msg: '正在启动执行，请稍后...' })
        break
      case 'startSuccess':
        $loading.close()
        message.success('启动执行成功')
        break
      case 'startFailed':
        $loading.close()
        message.error('启动失败，请稍后重试。')
        break
      case 'runSuccess':
        message.success('运行结束')
        break
      case 'runFailed':
        message.success('运行失败，请稍后重试。')
        break
      case 'stopping':
        break
      case 'stopSuccess':
        message.success('运行已停止')
        break
      case 'stopFailed':
        break
      default:
        break
    }
  })
}
