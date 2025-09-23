import { log } from './3rd/log'
/** @format */
import { wsApp } from './3rd/rpa_websocket'
import { bgHandler, contentMessageHandler } from './background/backgroundInject'
import { V2_EXTENSION_ID, V3_EXTENSION_ID } from './background/constant'

function getAllTabs() {
  return new Promise<chrome.tabs.Tab[]>((resolve) => {
    chrome.tabs.query({}, (tabs) => {
      resolve(tabs)
    })
  })
}

function reloadAllTabs() {
  getAllTabs().then((tabs: chrome.tabs.Tab[]) => {
    for (const tab of tabs) {
      chrome.tabs.reload(tab.id)
    }
  })
}

function getInstalledExtensions() {
  return new Promise<chrome.management.ExtensionInfo[]>((resolve) => {
    chrome.management.getAll((exts: chrome.management.ExtensionInfo[]) => {
      log.info('Installed extensions:', exts)
      resolve(exts)
    })
  })
}

function disableOldExtensions() {
  getInstalledExtensions().then((exts: chrome.management.ExtensionInfo[]) => {
    exts.forEach((ext) => {
      if (ext.id === V2_EXTENSION_ID || ext.id === V3_EXTENSION_ID) {
        chrome.management.setEnabled(ext.id, false)
      }
    })
  })
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  contentMessageHandler(request, sender, sendResponse)
  return true
})
chrome.runtime.onInstalled.addListener(() => {
  reloadAllTabs()
  disableOldExtensions()
})
chrome.runtime.onStartup.addListener(() => {
  reloadAllTabs()
})
chrome.management.onEnabled.addListener((info) => {
  if (info.id === chrome.runtime.id) {
    reloadAllTabs()
    disableOldExtensions()
  }
})

; (function () {
  wsApp.start()
  wsApp.event('browser', '', (msg) => {
    const newMsg = msg.to_reply()
    wsHandler(msg).then((result) => {
      newMsg.data = result
      wsApp.send(newMsg)
    })
  })
})()

async function wsHandler(message) {
  const msgObject = typeof message === 'string' ? JSON.parse(message) : message
  log.info(msgObject.key, msgObject)
  const result = await bgHandler(msgObject)
  log.info(msgObject.key, result)
  return result
}
