import { log } from '../3rd/log'

import { ErrorMessage } from './constant'
import { Utils } from './utils'

const isFirefox = Utils.getNavigatorUserAgent() === '$firefox$'

export function checkDebuggerDetached(tabId, attempts = 0) {
  return new Promise((resolve, reject) => {
    if (attempts > 10) {
      reject(new Error(ErrorMessage.DEBUGGER_TIMOUT))
      return
    }

    chrome.debugger.getTargets((targets) => {
      const stillAttached = targets.some(target => target.tabId === tabId)

      if (!stillAttached) {
        resolve(true)
      }
      else {
        setTimeout(() => checkDebuggerDetached(tabId, attempts + 1), 500)
      }
    })
  })
}

/**
 * Debugger-related functions
 * 1. attach debugger
 * 2. Listen for events and obtain the execution context
 * 3, execute the code
 * 4. detach debugger
 */
const Debugger = {
  attached: false,
  tabId: 0,
  frameContextIdMap: {
    0: [], // frameId 0 executionContextIds
  } as Record<string, number[]>, // frameId executionContextIds
  enableRuntime: (tabId: number) => {
    return new Promise((resolve, reject) => {
      chrome.debugger.sendCommand({ tabId }, 'Runtime.enable', {}, () => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          resolve(true)
        }
      })
    })
  },
  attachDebugger: (tabId: number) => {
    return new Promise((resolve, reject) => {
      if (Debugger.attached) {
        return reject(new Error('Debugger is already attached to a tab'))
      }
      chrome.debugger.attach({ tabId }, '1.3', () => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          log.info('Debugger attached successfully')
          Debugger.tabId = tabId
          Debugger.attached = true
          resolve(true)
        }
      })
    })
  },
  detachDebugger: (tabId: number) => {
    return new Promise((resolve) => {
      chrome.debugger.detach({ tabId }, () => {
        log.info('Debugger detached successfully')
        Debugger.attached = false
        Debugger.frameContextIdMap = { 0: [] }
        resolve(true)
      })
    })
  },
  getFrameTree: async (tabId: number) => {
    return new Promise((resolve, reject) => {
      chrome.debugger.sendCommand({ tabId }, 'Page.getFrameTree', {}, (result) => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          reject(chrome.runtime.lastError)
        }
        else {
          resolve(result)
        }
      })
    })
  },
  evaluate: async (tabId: number, code: string, frameId: number) => {
    code = `(function() { ${code} })()`

    await Debugger.attachDebugger(tabId)
    await Debugger.enableRuntime(tabId)
    await Utils.wait(1)

    const currentFrameContextIds = Debugger.frameContextIdMap[frameId] || []
    if (!currentFrameContextIds.length) {
      throw new Error(ErrorMessage.CONTEXT_NOT_FOUND)
    }
    const allPromise = currentFrameContextIds?.map(item => chrome.debugger.sendCommand({ tabId }, 'Runtime.evaluate', { expression: code, contextId: item }))
    const allRes = await Promise.all(allPromise)
    const successRes = allRes.find(item => !item.exceptionDetails)
    const failRes = allRes.find(item => item.exceptionDetails)
    log.info('evaluate successRes: ', successRes, 'evaluate failRes: ', failRes)
    await Debugger.detachDebugger(tabId)
    if (successRes) {
      return successRes.result.value || ''
    }
    else if (failRes) {
      throw new Error(failRes.result.description)
    }
    else {
      throw new Error(ErrorMessage.EXECUTE_ERROR)
    }
  },
}
/**
 * Listen to console.log to obtain the correspondence between frameId and executionContextId
 * The rpa_debugger_on code in the content will print the frameId
 */
if (!isFirefox) {
  chrome.debugger.onEvent.addListener(async (source, method, params) => {
    if (source.tabId !== Debugger.tabId)
      return
    if (method !== 'Runtime.consoleAPICalled' || params.type !== 'log' || !params.args?.length)
      return

    const logValue = params.args[0]?.value || ''
    const executionContextId = params.executionContextId

    if (logValue.includes('rpa_debugger_on')) {
      const frameId = `${logValue.split(':')[1]}`
      if (!Debugger.frameContextIdMap[frameId]) {
        Debugger.frameContextIdMap[frameId] = [executionContextId]
      }
      if (!Debugger.frameContextIdMap[frameId].includes(executionContextId)) {
        Debugger.frameContextIdMap[frameId].push(executionContextId)
      }
    }
  })
  chrome.debugger.onDetach.addListener(() => {
    Debugger.attached = false
  })
}

export { Debugger }
