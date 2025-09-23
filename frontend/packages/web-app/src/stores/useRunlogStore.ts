import dayjs from 'dayjs'
import { debounce } from 'lodash-es'
// 运行日志信息
import { defineStore } from 'pinia'
import { ref, shallowRef } from 'vue'

const LOG_LEVEL_MAP: Record<RPA.LogLevel, string> = {
  error: '错误',
  info: '信息',
  warning: '警告',
  debug: '调试',
}

function geneLogItem(it: RPA.ServerLogItem, index: number): RPA.LogItem {
  return {
    id: it.line_id || it.event_id || `row_${index}`,
    logLevel: it.log_level,
    logLevelText: LOG_LEVEL_MAP[it.log_level],
    timestamp: dayjs(it.event_time * 1000).format('YYYY-MM-DD HH:mm:ss'),
    content: it.msg_str,
    lineNum: it.line,
    processName: it.process,
    processId: it.process_id,
  }
}

export const useRunlogStore = defineStore('runlog', () => {
  const logList = shallowRef<RPA.LogItem[]>([])
  const activeLogId = ref('')
  const pendingLogs = shallowRef<RPA.ServerLogItem[]>([])

  const flushLogs = debounce(() => {
    const newLogs = pendingLogs.value.map((it, index) =>
      geneLogItem(it, logList.value.length + index),
    )

    logList.value = [...logList.value, ...newLogs]
    pendingLogs.value = []

    if (logList.value.length > 10000) { // 设置阈值，避免极端情况
      logList.value = logList.value.slice(-10000)
    }
  }, 300, { maxWait: 1000 })

  const addLog = (log: RPA.ServerLogItem) => {
    if (log.status === 'debug_start')
      return

    // 如果 logList 为空，立即添加第一条日志
    if (logList.value.length === 0) {
      logList.value.push(geneLogItem(log, 0))
      return
    }

    // 否则加入待处理队列
    pendingLogs.value.push(log)
    flushLogs()
  }

  const clearLogs = () => {
    logList.value = []
  }

  const setLogs = (data: Array<RPA.ServerLogItem>) => {
    logList.value = data.map((it, index) => geneLogItem(it, index))
  }

  const setActiveLogId = (id: string) => {
    activeLogId.value = id
  }

  return {
    activeLogId,
    logList,
    addLog,
    setLogs,
    clearLogs,
    setActiveLogId,
  }
})
