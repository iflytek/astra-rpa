import { Utils } from './utils'

const scale = 1
const quality = 92
const format = 'jpeg'
export async function captureFullPage(tab: chrome.tabs.Tab) {
  const isFirefox = Utils.getNavigatorUserAgent() === '$firefox$'
  let data

  if (isFirefox) {
    data = await fullPageShotFirefox(tab)
    return data
  }

  await attach(tab.id, null, tab)
  await enablePage(tab.id)
  await setBg(tab.id, { color: { r: 255, g: 255, b: 255, a: 1 } })
  const {
    cssContentSize: { width, height },
  } = await getSize(tab.id)
  await setSize(tab.id, { height, width })
  await sleep(500)
  data = await screenshot(tab.id, { x: 0, y: 0, width, height })
  await sleep(500)
  await clearSize(tab.id)
  await detach(tab.id)
  return data
}

function clearSize(tabId) {
  return new Promise((resolve) => {
    chrome.debugger.sendCommand(
      {
        tabId,
      },
      'Emulation.clearDeviceMetricsOverride',
      resolve,
    )
  })
}

function screenshot(tabId, area?: { x: number, y: number, width: number, height: number }) {
  return new Promise((resolve, reject) => {
    chrome.debugger.sendCommand(
      { tabId },
      'Page.captureScreenshot',
      {
        format,
        fromSurface: true,
        quality,
        clip: { ...area, scale },
      },
      (response) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError)
        }
        else {
          const base_64_data = `data:image/${format};base64,${response.data}`
          resolve(base_64_data)
        }
      },
    )
  })
}

function setSize(tabId, { height, width }) {
  return new Promise((resolve) => {
    chrome.debugger.sendCommand(
      {
        tabId,
      },
      'Emulation.setDeviceMetricsOverride',
      { height, width, deviceScaleFactor: scale, mobile: false },
      resolve,
    )
  })
}

function getSize(tabId): Promise<{ cssContentSize: { width: number, height: number } }> {
  return new Promise((resolve) => {
    chrome.debugger.sendCommand(
      {
        tabId,
      },
      'Page.getLayoutMetrics',
      {},
      resolve,
    )
  })
}

function setBg(tabId, bg) {
  return new Promise((resolve) => {
    chrome.debugger.sendCommand({ tabId }, 'Emulation.setDefaultBackgroundColorOverride', bg, resolve)
  })
}

function enablePage(tabId) {
  return new Promise((resolve) => {
    chrome.debugger.sendCommand({ tabId }, 'Page.enable', {}, () => {
      resolve(tabId)
    })
  })
}

function attach(tabId, _changeInfo, tab) {
  return new Promise((resolve, reject) => {
    if (tab.status === 'complete') {
      chrome.debugger.attach({ tabId }, '1.0', () => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError)
        }
        else {
          resolve(tab || { id: tabId })
        }
      })
    }
  })
}

function detach(tabId) {
  return new Promise((resolve) => {
    chrome.debugger.detach({ tabId }, () => {
      setTimeout(() => {
        resolve(tabId)
      }, 3000)
    })
  })
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms))
}

/**
 *  firefox support pageshot
 */

export function fullPageShotFirefox(tab) {
  return new Promise((resolve) => {
    chrome.tabs.sendMessage(
      tab.id,
      {
        key: 'fullPageRect',
        data: {},
      },
      {
        frameId: 0,
      },
      (rect) => {
        // @ts-expect-error browser is firefox entension api
        browser.tabs.captureTab(tab.id, {
          format,
          quality,
          rect,
        }).then((dataUri) => {
          resolve(dataUri)
        })
      },
    )
  })
}

export async function captureArea(tab: chrome.tabs.Tab, area: { x: number, y: number, width: number, height: number }) {
  const dpr = await getPageDevicePixelRatio(tab)
  area = {
    x: area.x / dpr,
    y: area.y / dpr,
    width: area.width / dpr,
    height: area.height / dpr,
  }
  await attach(tab.id, null, tab)
  await enablePage(tab.id)
  await setBg(tab.id, { color: { r: 255, g: 255, b: 255, a: 1 } })
  await sleep(3000)

  const data = await screenshot(tab.id, area)
  await clearSize(tab.id)
  await detach(tab.id)
  await sleep(1000)
  return data
}

export function resetScale(tabId) {
  return new Promise((resolve) => {
    chrome.tabs.setZoom(tabId, 1, () => {
      resolve(true)
    })
  })
}

export function getPageDevicePixelRatio(tab: chrome.tabs.Tab): Promise<number> {
  return new Promise((resolve) => {
    chrome.tabs.sendMessage(
      tab.id,
      {
        key: 'getDPR',
        data: {},
      },
      {
        frameId: 0,
      },
      (res) => {
        typeof res.dpr === 'number' ? resolve(res.dpr) : resolve(1)
      },
    )
  })
}
