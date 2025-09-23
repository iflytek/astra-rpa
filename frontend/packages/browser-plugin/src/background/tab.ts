import { ErrorMessage, StatusCode } from './constant'
import { Debugger } from './debugger'
import { captureArea, captureFullPage } from './full_page_shot'
import { Utils } from './utils'

const isFirefox = Utils.getNavigatorUserAgent() === '$firefox$'

export const Tabs = {
  query: (queryInfo): Promise<chrome.tabs.Tab[]> => {
    return new Promise<chrome.tabs.Tab[]>((resolve) => {
      chrome.tabs.query(queryInfo, (tabs) => {
        resolve(tabs)
      })
    })
  },
  create: (createInfo): Promise<chrome.tabs.Tab> => {
    if (!createInfo.url) {
      createInfo.url = 'about:blank'
    }
    return new Promise<chrome.tabs.Tab>((resolve) => {
      chrome.tabs.create(createInfo, (tab) => {
        resolve(tab)
      })
    })
  },
  update: (tabId: number, updateInfo): Promise<chrome.tabs.Tab> => {
    return new Promise<chrome.tabs.Tab>((resolve) => {
      chrome.tabs.update(tabId, updateInfo, (tab) => {
        resolve(tab)
      })
    })
  },
  get: (tabId: number): Promise<chrome.tabs.Tab> => {
    return new Promise<chrome.tabs.Tab>((resolve) => {
      chrome.tabs.get(tabId, (tab) => {
        resolve(tab)
      })
    })
  },
  reload: (): Promise<boolean> => {
    return new Promise<boolean>((resolve) => {
      Tabs.getActiveTab().then((tab) => {
        chrome.tabs.reload(
          tab.id,
          {
            bypassCache: true,
          },
          () => {
            resolve(true)
          },
        )
      })
    })
  },
  stopLoad: (): Promise<ContentResult> => {
    return new Promise<ContentResult>((resolve) => {
      Tabs.getActiveTab().then((tab) => {
        Tabs.sendTabMessage(tab.id, {
          key: 'stopLoad',
          data: {
            key: 'stopLoad',
            data: {},
          },
        }).then((response) => {
          resolve(response)
        })
      })
    })
  },
  goForward: (): Promise<boolean> => {
    return new Promise<boolean>((resolve) => {
      Tabs.getActiveTab().then((tab) => {
        chrome.tabs.goForward(tab.id, () => {
          resolve(true)
        })
      })
    })
  },
  goBack: (): Promise<boolean> => {
    return new Promise<boolean>((resolve) => {
      Tabs.getActiveTab().then((tab) => {
        chrome.tabs.goBack(tab.id, () => {
          resolve(true)
        })
      })
    })
  },
  remove: (tabIds: number | number[]): Promise<boolean> => {
    return new Promise<boolean>((resolve) => {
      chrome.tabs.remove(tabIds, () => {
        resolve(true)
      })
    })
  },
  getZoom: (tabId: number): Promise<number> => {
    return new Promise<number>((resolve) => {
      chrome.tabs.getZoom(tabId, (factor) => {
        resolve(factor)
      })
    })
  },
  executeFuncOnFrame: (
    tabId: number,
    frameId: number,
    funcCode: (...args: any[]) => void,
    args: any[],
  ): Promise<unknown> => {
    return new Promise((resolve, reject) => {
      chrome.scripting.executeScript(
        {
          target: { tabId, frameIds: [frameId] },
          func: funcCode,
          args,
          world: 'ISOLATED',
        },
        (result) => {
          if (chrome.runtime.lastError) {
            return reject(new Error(chrome.runtime.lastError.message))
          }
          if (!result || result[0] === null) {
            reject(new Error(`${funcCode.toString()}executeFuncOnFrame error on frameId${frameId}`))
          }
          else if (Array.isArray(result) && result.length === 1) {
            resolve(result[0].result)
          }
          else {
            reject(new Error(`unknown error: fail to execute script on ${frameId}`))
          }
        },
      )
    })
  },
  executeScriptOnFrame: (
    tabId: number,
    frameId: number,
    code: string,
  ): Promise<unknown> => {
    return new Promise((resolve, reject) => {
      Debugger.evaluate(tabId, code, frameId)
        .then((result) => {
          resolve(result)
        })
        .catch((error) => {
          Debugger.detachDebugger(tabId)
          reject(error)
        })
    })
  },
  runJS: (
    tabId: number,
    frameId: number,
    params: any,
  ): Promise<unknown> => {
    return new Promise((resolve, reject) => {
      if (isFirefox) {
        Tabs.sendTabFrameMessage(tabId, params, frameId).then((response) => {
          if (response.code === StatusCode.SUCCESS) {
            resolve(response.data)
          }
          else {
            reject(new Error(response.msg || ErrorMessage.EXECUTE_ERROR))
          }
        }).catch((error) => { reject(error) })
      }
      else {
        const { code } = params.data
        Tabs.executeScriptOnFrame(tabId, frameId, code).then((result) => {
          resolve(result)
        }, (error) => {
          reject(error)
        })
      }
    })
  },
  getAllTabs: (): Promise<chrome.tabs.Tab[]> => {
    return new Promise<chrome.tabs.Tab[]>((resolve) => {
      chrome.tabs.query({}, (tabs) => {
        resolve(tabs)
      })
    })
  },
  reloadAllTabs: (): void => {
    Tabs.getAllTabs().then((tabs: chrome.tabs.Tab[]) => {
      for (const tab of tabs) {
        if (tab.url && !tab.url.startsWith('chrome://')) {
          chrome.tabs.reload(tab.id)
        }
      }
    })
  },
  urlGetTab: (url: string): Promise<chrome.tabs.Tab> => {
    return new Promise<chrome.tabs.Tab>((resolve, reject) => {
      chrome.tabs.query({}, (tabs) => {
        const targetTab = tabs.find((tab) => {
          if (Utils.isEndWithSlash(tab.url) && !Utils.isEndWithSlash(url)) {
            return tab.url === `${url}/`
          }
          else {
            return tab.url === url
          }
        })
        if (targetTab) {
          Tabs.activeTargetTab(targetTab.id).then((tab) => {
            resolve(tab)
          })
        }
        else {
          reject(new Error('no tab found'))
        }
      })
    })
  },
  getTab: (url: string): Promise<chrome.tabs.Tab> => {
    return new Promise<chrome.tabs.Tab>((resolve, reject) => {
      try {
        Tabs.getActiveTab().then((tab) => {
          if (tab.url === url) {
            resolve(tab)
          }
          else {
            Tabs.urlGetTab(url).then(
              (tab) => {
                resolve(tab)
              },
              () => {
                Tabs.openTab(url).then((tab) => {
                  resolve(tab)
                })
              },
            )
          }
        })
      }
      catch (error) {
        reject(error)
      }
    })
  },
  getActiveTab: (): Promise<chrome.tabs.Tab> => {
    return new Promise<chrome.tabs.Tab>((resolve) => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        resolve(tabs[0])
      })
    })
  },
  activeTargetTab: (tabId: number): Promise<chrome.tabs.Tab> => {
    return new Promise<chrome.tabs.Tab>((resolve) => {
      chrome.tabs.update(tabId, { active: true }, (tab) => {
        resolve(tab)
      })
    })
  },
  activeTargetTabByTabUrl: (url: string): Promise<chrome.tabs.Tab> => {
    return new Promise<chrome.tabs.Tab>((resolve) => {
      chrome.tabs.query({ url }, (tabs) => {
        if (tabs && tabs[0]) {
          chrome.tabs.update(tabs[0].id, { active: true, highlighted: true, selected: true }, (tab) => {
            resolve(tab)
          })
        }
        else {
          chrome.tabs.create({ url }, (tab) => {
            resolve(tab)
          })
        }
      })
    })
  },
  switchTab: (url: string, title: string, id: number): Promise<chrome.tabs.Tab | null> => {
    return new Promise<chrome.tabs.Tab | null>((resolve) => {
      if (id) {
        Tabs.activeTargetTab(id).then((tab) => {
          resolve(tab)
        })
      }
      else {
        chrome.tabs.query({ url, title }, (tabs) => {
          if (tabs && tabs[0]) {
            Tabs.activeTargetTab(tabs[0].id).then((tab) => {
              resolve(tab)
            })
          }
          else {
            resolve(null)
          }
        })
      }
    })
  },
  openTab: (url: string): Promise<chrome.tabs.Tab> => {
    return new Promise<chrome.tabs.Tab>((resolve) => {
      chrome.tabs.create({ url }, (tab) => {
        resolve(tab)
      })
    })
  },
  closeTab: (tabId: number): Promise<boolean> => {
    return new Promise<boolean>((resolve) => {
      chrome.tabs.remove(tabId, () => {
        resolve(true)
      })
    })
  },
  excuteTabScript: (tabId: number, script: string): Promise<unknown> => {
    return new Promise((resolve) => {
      chrome.tabs.executeScript(tabId, { code: script }, (results) => {
        resolve(results)
      })
    })
  },
  getAllFrames: (tabId: number): Promise<FrameDetails[]> => {
    return new Promise<FrameDetails[]>((resolve) => {
      chrome.webNavigation.getAllFrames(
        {
          tabId,
        },
        (frames: FrameDetails[]) => {
          const supportFrames = frames.filter(frame => Utils.isSupportProtocal(frame.url))
          const promises = supportFrames.map((frame, index) => {
            const args = [{ frameId: frame.frameId }]
            return Tabs.executeFuncOnFrame(
              tabId,
              frame.frameId,
              (arg) => {
                // @ts-expect-error window in content script
                return window.handleSync({
                  key: 'getFrameInfo',
                  data: arg,
                })
              },
              args,
            ).then((result: CurrentFrameInfo) => {
              if (frame.frameId !== 0) {
                const { iframeXpath } = result
                supportFrames[index] = { ...frame, iframeXpath }
              }
              else {
                supportFrames[index] = { ...frame, iframeXpath: '' }
              }
            })
          })
          Promise.all(promises).then(() => resolve(supportFrames))
        },
      )
    })
  },
  getExtFrames: (tabId: number): Promise<FrameDetails[]> => {
    return new Promise<FrameDetails[]>((resolve) => {
      chrome.webNavigation.getAllFrames(
        {
          tabId,
        },
        (frames) => {
          resolve(frames)
        },
      )
    })
  },
  sendTabFrameMessage: (tabId: number, message, frameId: number): Promise<ContentResult> => {
    return new Promise<ContentResult>((resolve, reject) => {
      try {
        chrome.tabs.sendMessage(
          tabId,
          message,
          {
            frameId,
          },
          (response) => {
            resolve(response)
          },
        )
      }
      catch (error) {
        reject(error)
      }
    })
  },
  sendTabMessage: (tabId: number, message): Promise<ContentResult> => {
    return new Promise<ContentResult>((resolve) => {
      chrome.tabs.sendMessage(tabId, message, {}, (response) => {
        resolve(response)
      })
    })
  },
  sendMessage: (message): Promise<ContentResult> => {
    return new Promise<ContentResult>((resolve) => {
      Tabs.getAllTabs().then((tabs) => {
        tabs.forEach((tab) => {
          chrome.tabs.sendMessage(tab.id, message, {}, (response) => {
            resolve(response)
          })
        })
      })
    })
  },
  getFramePosition: (tabId: number, frameId: number, frameUrl: string): Promise<ContentResult> => {
    return new Promise<ContentResult>((resolve) => {
      Tabs.sendTabFrameMessage(
        tabId,
        {
          key: 'getFramePosition',
          data: { url: frameUrl },
        },
        frameId,
      ).then((response) => {
        resolve(response)
      })
    })
  },
  getUrl: (): Promise<string> => {
    return new Promise<string>((resolve) => {
      Tabs.getActiveTab().then((tab) => {
        resolve(tab.url)
      })
    })
  },
  getTitle: (): Promise<string> => {
    return new Promise<string>((resolve) => {
      Tabs.getActiveTab().then((tab) => {
        resolve(tab.title)
      })
    })
  },
  captureScreen: (): Promise<unknown> => {
    return new Promise<unknown>((resolve) => {
      Tabs.getActiveTab().then((tab) => {
        chrome.tabs.captureVisibleTab(tab.windowId, { format: 'jpeg', quality: 80 }, (dataUrl) => {
          resolve(dataUrl)
        })
      })
    })
  },
  capturePage: async (): Promise<unknown> => {
    return new Promise<unknown>((resolve) => {
      Tabs.getActiveTab().then((tab) => {
        captureFullPage(tab).then((data) => {
          resolve(data)
        })
      })
    })
  },
  captureElement: async (area: { x: number, y: number, width: number, height: number }): Promise<unknown> => {
    return new Promise<unknown>((resolve) => {
      Tabs.getActiveTab().then((tab) => {
        captureArea(tab, area).then((data) => {
          resolve(data)
        })
      })
    })
  },
  resetZoom: (tabId: number): Promise<boolean> => {
    return new Promise<boolean>((resolve) => {
      chrome.tabs.setZoom(tabId, 1, () => {
        resolve(true)
      })
    })
  },
}

export const WebNavigation = {
  getAllFrames: (tabId: number): Promise<FrameDetails[]> => {
    return new Promise<FrameDetails[]>((resolve) => {
      chrome.webNavigation.getAllFrames(
        {
          tabId,
        },
        (frames) => {
          resolve(frames)
        },
      )
    })
  },
}
