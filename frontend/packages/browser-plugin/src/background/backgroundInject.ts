import { log } from '../3rd/log'
import type { BatchElementParams } from '../types/data_batch.d'

import { ErrorMessage, StatusCode } from './constant'
import { Cookie } from './cookie'
import DataTable from './data_table'
import { getSimilarElement, isSameIdStart } from './similar'
import { Tabs } from './tab'
import { Utils } from './utils'
import { WindowControl } from './window'

globalThis.activeElement = null

function contentMessageHandler(request, sender: chrome.runtime.MessageSender, _sendResponse: () => void) {
  if (request.type === 'element' && sender.tab) {
    const info = {
      tabTitle: sender.tab.title,
      tabUrl: sender.tab.url,
      // favIconUrl: sender.tab.favIconUrl,// different in chrome and firefox
      isFrame: sender.frameId !== 0,
      frameId: sender.frameId,
    }
    globalThis.activeElement = { ...request.data, ...info }
  }
  return true
}

async function processFrames(tab: chrome.tabs.Tab, framePath: number[], p: Point, activeElement: ElementInfo) {
  const iframeDepthInfo = []
  for (const frame of framePath) {
    try {
      const res = await Tabs.executeFuncOnFrame(tab.id, frame, (arg) => {
        // @ts-expect-error window in content_script
        return window.handleSync({
          key: 'getIframeElement',
          data: arg,
        })
      }, [p])

      iframeDepthInfo.push(res)
      const { nextPos } = res as { nextPos: Point }
      p.x = nextPos.x
      p.y = nextPos.y
    }
    catch {
      return [activeElement]
    }
  }
  return iframeDepthInfo
}

async function getIframeElement(p: Point, activeElement: ElementInfo) {
  const tab = await Tabs.getActiveTab()
  const frames = await Tabs.getAllFrames(tab.id)
  const iframeElementInfo = JSON.parse(JSON.stringify(activeElement))

  let targetFrame = frames.find(frame => frame.frameId === activeElement.frameId)
  const framePath: number[] = []
  // get the position of the frame relative to the parent frame
  while (targetFrame) {
    framePath.unshift(targetFrame.frameId)
    targetFrame = frames.find(frame => frame.frameId === targetFrame.parentFrameId)
  }
  const iframeDepthInfo = await processFrames(tab, framePath, p, activeElement)

  if (iframeDepthInfo.length > 0) {
    const lastElement = iframeDepthInfo[iframeDepthInfo.length - 1]
    const isPathEqual = lastElement.xpath === activeElement.xpath
    const isUrlEqual = lastElement.url === activeElement.url
    if (!isPathEqual || !isUrlEqual) {
      iframeDepthInfo[iframeDepthInfo.length - 1] = iframeElementInfo
    }
    iframeDepthInfo.forEach((frameInfo, index) => {
      if (index === 0) {
        iframeElementInfo.iframeXpath = frameInfo.xpath
      }
      else {
        iframeElementInfo.iframeXpath = `${iframeElementInfo.iframeXpath}/$iframe$${frameInfo.xpath}`
      }
      if (frameInfo.iframeContentRect) {
        iframeElementInfo.rect.x += frameInfo.iframeContentRect.x
        iframeElementInfo.rect.y += frameInfo.iframeContentRect.y
      }
    })
    // iframeElementInfo left, top, right, bottom,
    iframeElementInfo.rect.left = iframeElementInfo.rect.x
    iframeElementInfo.rect.top = iframeElementInfo.rect.y
    iframeElementInfo.rect.right = iframeElementInfo.rect.x + iframeElementInfo.rect.width
    iframeElementInfo.rect.bottom = iframeElementInfo.rect.y + iframeElementInfo.rect.height

    iframeElementInfo.iframeXpath = iframeElementInfo.iframeXpath.split('/$iframe$').slice(0, -1).join('/$iframe$')

    return iframeElementInfo
  }
  else {
    return activeElement
  }
}

function findFrameByUrl(frames: FrameDetails[], url: string) {
  return frames.find(frame => frame.url.includes(url))
}

function findFrameByXpath(frames: FrameDetails[], iframeXpath: string) {
  if (!iframeXpath || !Array.isArray(frames) || frames.length === 0)
    return null

  const segments = iframeXpath
    .split('/$iframe$')
    .map(s => s.trim())
    .filter(Boolean)
  if (segments.length === 0)
    return null

  const rootFrame = frames.find(f => f.frameId === 0)
  if (!rootFrame)
    return null

  let current: FrameDetails | null = rootFrame
  for (const seg of segments) {
    const next = frames.find(f => f.iframeXpath === seg && f.parentFrameId === current!.frameId)
    if (!next)
      return null
    current = next
  }
  return current
}

function getFramePath(frames: FrameDetails[], targetFrame: FrameDetails) {
  const framePath: FrameDetails[] = []
  while (targetFrame) {
    framePath.unshift(targetFrame)
    targetFrame = frames.find(frame => frame.frameId === targetFrame.parentFrameId)
  }
  return framePath
}

async function calculateAbsolutePosition(tabId: number, framePath: FrameDetails[]) {
  const posPromises = framePath.slice(0, -1).map((frame, index) => {
    const nextFrame = framePath[index + 1]
    const args = [{
      iframeXpath: nextFrame.iframeXpath,
      url: nextFrame.url,
    }]
    return Tabs.executeFuncOnFrame(tabId, frame.frameId, (arg) => {
      // @ts-expect-error window in content_script
      return window.handleSync({
        key: 'getFramePosition',
        data: arg,
      })
    }, args)
  })

  const posRes = await Promise.all(posPromises) as Point[]
  return posRes.reduce(
    (acc, pos) => {
      acc.x += pos.x
      acc.y += pos.y
      return acc
    },
    { x: 0, y: 0 },
  )
}

function adjustPosition(rect: DOMRectT | DOMRectT[], absolutePos: Point) {
  if (Array.isArray(rect)) {
    rect.forEach(r => adjustRectPosition(r, absolutePos))
  }
  else {
    adjustRectPosition(rect, absolutePos)
  }
}

function adjustRectPosition(rect: DOMRectT, absolutePos: Point) {
  rect.x += absolutePos.x
  rect.y += absolutePos.y
  rect.left = rect.x
  rect.top = rect.y
  rect.right = rect.x + rect.width
  rect.bottom = rect.y + rect.height
}

async function findTabAndFrame(params: ElementParams) {
  const { url, iframeXpath, isFrame, tabUrl } = params.data
  let tab = await Tabs.getActiveTab()
  if (!tab) {
    tab = await Tabs.activeTargetTabByTabUrl(tabUrl)
    if (!tab) {
      throw new Error(ErrorMessage.ACTIVE_TAB_ERROR)
    }
  }
  if (!isFrame) {
    return { tab, frameId: 0 }
  }
  else {
    const frames = await Tabs.getAllFrames(tab.id)
    const targetFrame = iframeXpath ? findFrameByXpath(frames, iframeXpath) : findFrameByUrl(frames, url)
    if (targetFrame) {
      return { tab, frameId: targetFrame.frameId }
    }
    else {
      return { tab, frameId: Number.NaN }
    }
  }
}

const Handlers = {
  version: '5.1.7',
  tabsHandler() {
    return {
      async reloadTab() {
        const res = await Tabs.reload()
        return Utils.success(res)
      },
      async stopLoad() {
        const res = await Tabs.stopLoad()
        return Utils.success(res)
      },
      async openNewTab(params) {
        const tab = await Tabs.create(params.data)
        return Utils.success(tab)
      },
      async closeTab(params) {
        let { url, id } = params.data
        let tab: chrome.tabs.Tab
        if (id && typeof id !== 'number') {
          try {
            id = Number.parseInt(id, 10)
            if (Number.isNaN(id)) {
              return Utils.fail(ErrorMessage.NUMBER_ID_ERROR)
            }
          }
          catch {
            return Utils.fail(ErrorMessage.NUMBER_ID_ERROR)
          }
          await Tabs.remove(id)
          return Utils.success(true)
        }
        if (url) {
          tab = await Tabs.getTab(url)
        }
        if (!tab) {
          tab = await Tabs.getActiveTab()
        }
        if (!tab) {
          return Utils.fail('tab not found')
        }
        await Tabs.remove(tab.id)
        return Utils.success(true)
      },
      async updateTab(params) {
        const { url } = params.data
        const tab = await Tabs.getActiveTab()
        if (tab) {
          await Tabs.update(tab.id, { url })
          return Utils.success(true)
        }
        else {
          return Utils.fail('tab not found')
        }
      },
      async activeTab(params) {
        const { url } = params.data
        const tab = await Tabs.getTab(url)
        await Tabs.activeTargetTab(tab.id)
        return Utils.success(true)
      },
      async getActiveTab() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        return Utils.success(tab)
      },
      async switchTab(params) {
        let { url, title, id } = params.data
        if (id && typeof id !== 'number') {
          try {
            id = Number.parseInt(id, 10)
            if (Number.isNaN(id)) {
              return Utils.fail(ErrorMessage.NUMBER_ID_ERROR)
            }
          }
          catch {
            return Utils.fail(ErrorMessage.NUMBER_ID_ERROR)
          }
        }
        const tab = await Tabs.switchTab(url, title, id)
        if (tab) {
          return Utils.success(tab)
        }
        else {
          return Utils.fail(ErrorMessage.TAB_GET_ERROR)
        }
      },

      async getAllTabs() {
        const tabs = await Tabs.getAllTabs()
        return Utils.success(tabs)
      },

      async backward() {
        const res = await Tabs.goBack()
        return Utils.success(res)
      },
      async forward() {
        const res = await Tabs.goForward()
        return Utils.success(res)
      },

      async maxWindow() {
        const wind = await WindowControl.getCurrent()
        const maxWin = await WindowControl.update(wind.id, {
          state: 'maximized',
        })
        if (maxWin) {
          return Utils.success(true)
        }
        const { lastError } = chrome.runtime
        if (lastError) {
          return Utils.fail(lastError.message, StatusCode.EXECUTE_ERROR)
        }
      },
      async minWindow() {
        const wind = await WindowControl.getCurrent()
        const minWin = await WindowControl.update(wind.id, {
          state: 'minimized',
        })
        if (minWin) {
          return Utils.success(true)
        }
        const { lastError } = chrome.runtime
        if (lastError) {
          return Utils.fail(lastError.message, StatusCode.EXECUTE_ERROR)
        }
      },
      async executeScriptOnFrame(params) {
        const { url, code } = params.data
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const frames = await Tabs.getAllFrames(tab.id)
        const frame = frames.find(frame => frame.url === url)
        const frameId = frame ? frame.frameId : 0
        const res = await Tabs.executeScriptOnFrame(tab.id, frameId, code)
        return Utils.success(res)
      },
      async getTitle() {
        const title = await Tabs.getTitle()
        return Utils.success(title)
      },
      async getUrl() {
        const title = await Tabs.getUrl()
        return Utils.success(title)
      },
      async captureScreen() {
        const res = await Tabs.captureScreen()
        if (res) {
          return Utils.success(res)
        }
      },
      async capturePage() {
        const res = await Tabs.capturePage()
        if (res) {
          return Utils.success(res)
        }
      },
      async loadComplete() {
        const { lastError } = chrome.runtime
        const activeTab = await Tabs.getActiveTab()
        if (!activeTab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        if (lastError) {
          return Utils.fail(lastError.message, StatusCode.EXECUTE_ERROR)
        }
        if (activeTab.status === 'complete') {
          return Utils.success(true)
        }
        else {
          return Utils.success(false)
        }
      },
      async getFrames() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const frames = await Tabs.getAllFrames(tab.id)
        return frames
      },
      async getExtFrames() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const frames = await Tabs.getExtFrames(tab.id)
        return frames
      },
      async resetZoom() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const res = await Tabs.resetZoom(tab.id)
        return res
      },
      async getTabId() {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        return Utils.success(tab.id)
      },
    }
  },

  elementHandler() {
    return {
      async getElement(params) {
        const activeElement = globalThis.activeElement
        if (activeElement && activeElement.isFrame) {
          const { x, y } = params.data
          if (!x || !y) {
            return Utils.success(activeElement)
          }
          const result = await getIframeElement({ x, y }, activeElement)
          return Utils.success(result)
        }
        return Utils.success(activeElement)
      },
      async handleInContent(params: ElementParams) {
        const { tab, frameId } = await findTabAndFrame(params)
        if (Number.isNaN(frameId)) {
          return Utils.fail(ErrorMessage.FRAME_GET_ERROR, StatusCode.ELEMENT_NOT_FOUND)
        }
        if (!Utils.isSupportProtocal(tab.url)) {
          return Utils.fail(`${tab.url} ${ErrorMessage.CURRENT_TAB_UNSUPPORT_ERROR}`)
        }
        const result = await Tabs.sendTabFrameMessage(tab.id, params, frameId)
        if (result.code !== StatusCode.SUCCESS) {
          return Utils.fail(result.msg, result.code)
        }
        else {
          return Utils.success(result.data)
        }
      },
      async getElementPos(params: ElementParams) {
        const { url, isFrame, iframeXpath, tabUrl } = params.data
        let tab = await Tabs.getActiveTab()
        if (!tab) {
          tab = await Tabs.activeTargetTabByTabUrl(tabUrl)
        }
        if (!Utils.isSupportProtocal(tab.url)) {
          return Utils.fail(`${tab.url} ${ErrorMessage.CURRENT_TAB_UNSUPPORT_ERROR}`)
        }
        if (!isFrame) {
          const result = await Tabs.sendTabFrameMessage(tab.id, params, 0)
          return Utils.result(result.data, result.msg, result.code)
        }

        const frames = await Tabs.getAllFrames(tab.id)
        const targetFrame = iframeXpath ? findFrameByXpath(frames, iframeXpath) : findFrameByUrl(frames, url)

        if (!targetFrame) {
          return Utils.fail(ErrorMessage.FRAME_GET_ERROR, StatusCode.ELEMENT_NOT_FOUND)
        }

        const framePath = getFramePath(frames, targetFrame)

        const absolutePos = await calculateAbsolutePosition(tab.id, framePath)

        const elementPosResult = await Tabs.sendTabFrameMessage(tab.id, params, targetFrame.frameId)

        if (elementPosResult.code !== StatusCode.SUCCESS) {
          return Utils.fail(elementPosResult.msg, elementPosResult.code)
        }

        adjustPosition(elementPosResult.data.rect, absolutePos)

        return Utils.success(elementPosResult.data)
      },
      async checkElement(params: ElementParams) {
        const res = await Handlers.elementHandler().getElementPos(params)
        return res
      },
      async scrollIntoView(params: ElementParams) {
        if (params.data?.openSourcePage) {
          const activeTab = await Tabs.getActiveTab()
          if (!activeTab || activeTab.url !== params.data.tabUrl) {
            await Tabs.openTab(params.data.url)
          }
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async similarElement(params: ElementParams) {
        let activeElement = globalThis.activeElement
        const { tabUrl } = params.data
        let activeTab = await Tabs.getActiveTab()
        if (!activeTab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        if (activeTab.url !== tabUrl) {
          activeTab = await Tabs.getTab(tabUrl)
        }
        try {
          const isSameId = isSameIdStart(params.data.pathDirs, activeElement.pathDirs)
          if (!isSameId) {
            const res = await Handlers.elementHandler().handleInContent({
              ...params,
              key: 'reSimilarElement',
              data: { ...activeElement, preData: params.data },
            })
            log.info('reSimilarElement result: ', res)
            if (res.data) {
              params.data = res.data.preData
              activeElement = res.data
              delete params.data.preData
            }
          }
          const similarElementInfo = getSimilarElement(params.data, activeElement)
          if (similarElementInfo) {
            const res = await Handlers.elementHandler().handleInContent({
              ...params,
              data: similarElementInfo,
            })
            similarElementInfo.similarCount = res.data?.similarCount || 0
            return Utils.success(similarElementInfo)
          }
          else {
            return Utils.fail(ErrorMessage.NOT_SIMILAR_ELEMENT, StatusCode.ELEMENT_NOT_FOUND)
          }
        }
        catch (error) {
          return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
        }
      },

      async elementFromSelect(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async elementIsRender(params: ElementParams) {
        const { tab, frameId } = await findTabAndFrame(params)
        if (Number.isNaN(frameId)) {
          return Utils.success(false)
        }
        const result = await Tabs.sendTabFrameMessage(tab.id, params, frameId)
        if (result) {
          return Utils.success(result.data)
        }
        else {
          return Utils.success(false)
        }
      },

      async elementIsReady(params: ElementParams) {
        const activeTab = await Tabs.getActiveTab()
        const { tab, frameId } = await findTabAndFrame(params)
        if (Number.isNaN(frameId)) {
          return Utils.success(false)
        }
        params.key = 'elementIsRender'
        const result = await Tabs.sendTabFrameMessage(tab.id, params, frameId)
        const complete = activeTab.status === 'complete'
        if (result) {
          return Utils.success(result.data && complete)
        }
        else {
          return Utils.success(false)
        }
      },

      async elementIsTable(params: ElementParams) {
        if (!params.data.xpath) {
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        const isTable = !!res.data
        const elementResult = { isTable, ...params.data }
        return Utils.success(elementResult)
      },

      async tableDataBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        const values = res.data?.values || []
        const dataTable = new DataTable(res.data, values, 'table')
        const table = dataTable.getTable()
        return Utils.success(table)
      },

      async tableColumnDataBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        const value = res.data?.value || []
        const dataTable = new DataTable(res.data, value, 'similar')
        const table = dataTable.getTable()
        return Utils.success(table)
      },

      async similarBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          params.data = globalThis.activeElement
        }
        if ('batchType' in params.data && ['similar', 'similarAdd'].includes(params.data.batchType)) {
          const res = await Handlers.elementHandler().similarElement(params)
          if (res.code !== StatusCode.SUCCESS) {
            return res
          }
          params.data = res.data
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        const value = res.data?.value || []
        const dataTable = new DataTable(res.data, value, 'similar')
        const table = dataTable.getTable()
        return Utils.success(table)
      },

      async tableHeaderBatch(params: ElementParams) {
        if (!('xpath' in params.data)) {
          params.data = globalThis.activeElement
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async simalarListBatch(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async highLightColumn(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getBatchData(params: { key: string, data: BatchElementParams }) {
        if (params.data?.openSourcePage) {
          const activeTab = await Tabs.getActiveTab()
          if (!activeTab || activeTab.url !== params.data.tabUrl) {
            await Tabs.openTab(params.data.tabUrl)
          }
        }
        await Utils.wait(3)
        if (params.data && params.data.produceType === 'similar') {
          params.key = 'simalarListBatch'
          const res = await Handlers.elementHandler().simalarListBatch(params)
          return res
        }
        else {
          params.key = 'tableDataBatch'
          const res = await Handlers.elementHandler().tableDataBatch(params)
          return res
        }
      },

      async elementShot(params: ElementParams) {
        // 1, scrollToTop 2, resetZoom 3, getElementPos 4, debugger attach  5, capture 6, debugger detach 7, return data
        params.key = 'scrollToTop'
        await Handlers.elementHandler().scrollToTop(params)
        await Handlers.tabsHandler().resetZoom()
        params.key = 'getElementPos'
        const res = await Handlers.elementHandler().getElementPos(params)
        const { x, y, width, height } = res.data?.rect
        const data = await Tabs.captureElement({ x, y, width, height })
        return Utils.success(data)
      },

      async scrollToTop(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return Utils.success(res)
      },

      async getSimilarIterator(params: ElementParams) {
        params.key = 'elementFromSelect'
        const index = params.data?.index || 0
        const count = params.data?.count || 1
        const res = await Handlers.elementHandler().elementFromSelect(params)
        if (res.data && Array.isArray(res.data)) {
          if (index < res.data.length) {
            let data = [res.data[index]]
            if (index + count <= res.data.length) {
              data = res.data.slice(index, index + count)
            }
            else {
              data = res.data.slice(index)
            }
            data = data.map((item, index) => {
              item.index += index
              return { ...item, similarCount: res.data.length }
            })
            return Utils.success(data)
          }
          else {
            return Utils.success([])
          }
        }
        else {
          return Utils.fail(ErrorMessage.SIMILAR_NOT_FOUND, StatusCode.ELEMENT_NOT_FOUND)
        }
      },

      async getRelativeElement(params: ElementParams) {
        const { relativeOptions } = params.data
        if (!relativeOptions) {
          return Utils.fail(ErrorMessage.RELATIVE_ELEMENT_PARAMS_ERROR)
        }
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async generateElement(params: { key: string, data: GenerateParamsT }) {
        const tab = await Tabs.getActiveTab()
        if (!tab) {
          return Utils.fail(ErrorMessage.ACTIVE_TAB_ERROR)
        }
        const result = await Tabs.sendTabFrameMessage(tab.id, params, 0)
        return result
      },

      async clickElement(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async inputElement(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getElementText(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getElementAttrs(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async removeElementAttr(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async setElementAttr(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getElementChecked(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async setElementChecked(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getElementSelected(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async setElementSelected(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async getTableData(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },

      async scrollWindow(params: ElementParams) {
        const res = await Handlers.elementHandler().handleInContent(params)
        return res
      },
    }
  },

  jsHandler() {
    return {

      async runJS(params: ElementParams) {
        const { tab, frameId } = await findTabAndFrame(params)
        if (Number.isNaN(frameId)) {
          return Utils.fail(ErrorMessage.FRAME_GET_ERROR, StatusCode.ELEMENT_NOT_FOUND)
        }
        await Tabs.getAllFrames(tab.id)
        try {
          const result = await Tabs.runJS(tab.id, frameId, params)
          return Utils.success(result)
        }
        catch (error) {
          return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
        }
      },
    }
  },

  cookieHandler() {
    return { ...Cookie }
  },

  otherHandler() {
    return {
      currentExtension() {
        return new Promise((resolve) => {
          chrome.management.getSelf((info) => {
            resolve(info)
          })
        })
      },
      backgroundInject() {
        return Utils.success(true)
      },
      contentInject() {
        return Utils.success(true)
      },
    }
  },

  noHandler() {
    return Utils.fail(ErrorMessage.UNSUPPORT_ERROR)
  },
}

async function bgHandler(params) {
  let result = null
  const { key } = params
  const handlers = Handlers
  try {
    if (handlers[key]) {
      result = await handlers[key](params)
      return result
    }
    else if (handlers.tabsHandler()[key]) {
      result = await handlers.tabsHandler()[key](params)
      return result
    }
    else if (handlers.elementHandler()[key]) {
      if (params.data && 'produceType' in params.data && params.data.produceType === 'similar') {
        params.data = { ...params.data, ...params.data.values[0] }
      }
      result = await handlers.elementHandler()[key](params)
      return result
    }
    else if (handlers.jsHandler()[key]) {
      result = await handlers.jsHandler()[key](params)
      return result
    }
    else if (handlers.cookieHandler()[key]) {
      result = await handlers.cookieHandler()[key](params.data)
      return result
    }
    else if (handlers.otherHandler()[key]) {
      result = await handlers.otherHandler()[key](params.data)
      return result
    }
    else {
      result = handlers.noHandler()
      return result
    }
  }
  catch (error) {
    return Utils.fail(error.toString(), StatusCode.EXECUTE_ERROR)
  }
}

export { bgHandler, contentMessageHandler, Handlers }
