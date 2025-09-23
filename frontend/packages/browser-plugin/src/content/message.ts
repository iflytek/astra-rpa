function isExtensionContextValid() {
  try {
    return !!(chrome.runtime && chrome.runtime.id)
  }
  catch (error) {
    console.error('Error checking extension context:', error)
    return false
  }
}
export function sendToBackground(message) {
  return new Promise((resolve, reject) => {
    if (!isExtensionContextValid()) {
      resolve('Extension context is not valid')
      return
    }
    try {
      chrome.runtime.sendMessage(message, (response) => {
        resolve(response)
      })
    }
    catch (error) {
      reject(error)
    }
  })
}

export function sendElementData(elementData) {
  sendToBackground({
    type: 'element',
    data: elementData,
  })
}

export function sendLog(data) {
  sendToBackground({
    type: 'log',
    data,
  })
}
