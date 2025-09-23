import { vi } from 'vitest'

vi.stubGlobal('chrome', {
  tabs: {
    query: vi.fn((queryInfo, callback) => {
      if (queryInfo && queryInfo.active && queryInfo.currentWindow) {
        callback([{ id: 1, title: 'Active Tab', url: 'https://test.com', windowId: 1 }])
      }
      else if (queryInfo && queryInfo.url) {
        callback([{ id: 2, title: 'Tab By Url', url: queryInfo.url, windowId: 1 }])
      }
      else {
        callback([
          { id: 1, title: 'Tab1', url: 'https://test.com', windowId: 1 },
          { id: 2, title: 'Tab2', url: 'https://test2.com', windowId: 1 },
        ])
      }
    }),
    get: vi.fn((tabId, callback) => {
      callback && callback({ id: tabId, title: `Tab${tabId}`, url: `https://tab${tabId}.com`, windowId: 1 })
    }),
    reload: vi.fn((tabId, options, callback) => {
      if (typeof options === 'function') {
        callback = options
      }
      callback && callback()
    }),
    goForward: vi.fn((tabId, callback) => {
      callback && callback()
    }),
    goBack: vi.fn((tabId, callback) => {
      callback && callback()
    }),
    remove: vi.fn((tabIds, callback) => {
      callback && callback()
    }),
    create: vi.fn((createProperties, callback) => {
      callback && callback({ id: 2, ...createProperties })
    }),
    update: vi.fn((tabId, updateProperties, callback) => {
      callback && callback({ id: tabId, ...updateProperties })
    }),
    getZoom: vi.fn((tabId, callback) => {
      callback && callback(1)
    }),
    setZoom: vi.fn((tabId, zoomFactor, callback) => {
      callback && callback()
    }),
    executeScript: vi.fn((tabId, details, callback) => {
      callback && callback(['script result'])
    }),
    captureVisibleTab: vi.fn((windowId, options, callback) => {
      callback && callback('data:image/jpeg;base64,mockdata')
    }),
  },
  scripting: {
    executeScript: vi.fn((injection, callback) => {
      callback && callback([{ result: 'ok' }])
    }),
  },
  runtime: {
    lastError: null,
    sendMessage: vi.fn((message, options, callback) => {
      if (typeof options === 'function') {
        callback = options
      }
      callback && callback({ result: 'success' })
    }),
    onMessage: {
      addListener: vi.fn(),
      removeListener: vi.fn(),
    },
    getURL: vi.fn(path => `chrome-extension://extensionid/${path}`),
    getManifest: vi.fn(() => ({ name: 'Test Extension', version: '1.0.0' })),
    id: 'extensionid',
  },
  windows: {
    getCurrent: vi.fn((getInfo, callback) => {
      callback && callback({ id: 1, focused: true })
    }),
    create: vi.fn((createData, callback) => {
      callback && callback({ id: 2, ...createData })
    }),
  },
  debugger: {
    attach: vi.fn((target, version, callback) => {
      callback && callback()
    }),
    detach: vi.fn((target, callback) => {
      callback && callback()
    }),
    sendCommand: vi.fn((target, method, params, callback) => {
      if (method === 'Runtime.enable') {
        callback && callback({})
      }
      else if (method === 'Page.getFrameTree') {
        callback && callback({ frameTree: { frame: { id: 'main', url: 'https://test.com' }, childFrames: [] } })
      }
      else if (method === 'Runtime.evaluate') {
        callback && callback({ result: { value: 'mocked' } })
      }
      else {
        callback && callback({})
      }
    }),
    getTargets: vi.fn((callback) => {
      callback && callback([])
    }),
    onEvent: {
      addListener: vi.fn(),
      removeListener: vi.fn(),
    },
    onDetach: {
      addListener: vi.fn(),
      removeListener: vi.fn(),
    },
  },
})
