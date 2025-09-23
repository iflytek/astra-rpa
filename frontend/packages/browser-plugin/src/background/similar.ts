/**
 * Determine whether elements are similar based on the element information.
 * If they are similar, return the information of similar elements
 */
export function getSimilarElement(preElementInfo: ElementInfo, currentElementInfo: ElementInfo) {
  if (!isSimilarElement(preElementInfo, currentElementInfo)) {
    return false
  }
  const xpath = generateSimilarXapth(preElementInfo.xpath, currentElementInfo.xpath)

  const cssSelector = generateSimilarSelector(preElementInfo.cssSelector, currentElementInfo.cssSelector)

  const pathDirs = generateSimilarPathDirs(preElementInfo.pathDirs, currentElementInfo.pathDirs)

  const similarElementInfo = { ...preElementInfo, xpath, cssSelector, pathDirs }
  return similarElementInfo
}

export function isSimilarElement(preElementInfo: ElementInfo, currentElementInfo: ElementInfo) {
  const { xpath, cssSelector, pathDirs } = preElementInfo
  const { xpath: currentXpath, cssSelector: currentCssSelector, pathDirs: currentPathDirs } = currentElementInfo
  const xpathArr = xpath.split('/')
  const currentXpathArr = currentXpath.split('/')
  const cssSelectorArr = cssSelector.split('>')
  const currentCssSelectorArr = currentCssSelector.split('>')

  if (preElementInfo.url !== currentElementInfo.url) {
    return false
  }
  if (xpathArr.length !== currentXpathArr.length) {
    return false
  }

  if (xpathArr.length === currentXpathArr.length) {
    for (let i = 0; i < xpathArr.length; i++) {
      const leftTag = xpathArr[i]?.split('[')[0]
      const rightTag = currentXpathArr[i]?.split('[')[0]
      if (leftTag !== rightTag && leftTag !== '*' && rightTag !== '*') {
        return false
      }
    }
  }

  if (cssSelectorArr.length !== currentCssSelectorArr.length) {
    return false
  }

  if (pathDirs.length !== currentPathDirs.length) {
    return false
  }

  return true
}

export function generateSimilarXapth(preXpath: string, currentXpath: string) {
  if (preXpath === currentXpath) {
    return preXpath
  }
  const preXpathArr = preXpath.split('/')
  const currentXpathArr = currentXpath.split('/')
  for (let i = 0; i < preXpathArr.length; i++) {
    if (preXpathArr[i] !== currentXpathArr[i]) {
      preXpathArr[i] = preXpathArr[i]?.split('[')[0]
    }
  }
  const xpath = preXpathArr.join('/')
  return xpath
}

export function generateSimilarSelector(preSelector: string, currentSelector: string) {
  if (preSelector === currentSelector) {
    return preSelector
  }
  const preSelectorArr = preSelector.split('>')
  const currentSelectorArr = currentSelector.split('>')
  for (let i = 0; i < preSelectorArr.length; i++) {
    // nth-child
    if (preSelectorArr[i] !== currentSelectorArr[i] && preSelectorArr[i].includes(':nth-child')) {
      preSelectorArr[i] = preSelectorArr[i].split(':nth-child')[0]
    }
    // class
    if (preSelectorArr[i] !== currentSelectorArr[i] && preSelectorArr[i].includes('.')) {
      preSelectorArr[i] = preSelectorArr[i].split('.')[0]
    }
    // id #
    if (preSelectorArr[i] !== currentSelectorArr[i] && preSelectorArr[i].includes('#')) {
      preSelectorArr[i] = preSelectorArr[i].split('#')[0]
    }
  }
  const selector = preSelectorArr.join('>')
  return selector
}

export function generateSimilarPathDirs(prePathDirs: Array<ElementDirectory>, currentPathDirs: Array<ElementDirectory>) {
  for (let i = prePathDirs.length - 1; i >= 0; i--) {
    const prePathDir = prePathDirs[i]
    const currentPathDir = currentPathDirs[i]
    prePathDir.attrs.forEach((attr) => {
      attr.checked = false
      const currentAttr = currentPathDir.attrs.find(item => item.name === attr.name)
      if (!currentAttr) {
        attr.value = ''
      }
      if (currentAttr && currentAttr.name === 'id' && attr.value === currentAttr.value && attr.value !== '') {
        attr.checked = true
      }
      if (currentAttr && currentAttr.name === 'index' && attr.value !== '' && String(attr.value) === String(currentAttr.value)) {
        attr.checked = true
      }
      if (currentAttr && currentAttr.name === 'innertext') {
        attr.checked = false
        attr.value = ''
      }
    })
    const idChecked = prePathDir.attrs.some(item => item.name === 'id' && item.checked)
    if (idChecked) {
      prePathDir.attrs.forEach((attr) => {
        if (attr.name !== 'id') {
          attr.checked = false
        }
      })
    }
  }
  return prePathDirs
}

export function isSameIdStart(prePathDirs: Array<ElementDirectory>, currentPathDirs: Array<ElementDirectory>) {
  if (!prePathDirs || !currentPathDirs) {
    return false
  }
  if (prePathDirs.length === 0 || currentPathDirs.length === 0) {
    return false
  }
  const preFirst = prePathDirs[0]
  const currentFirst = currentPathDirs[0]
  const preIdAttr = preFirst.attrs.find(item => item.name === 'id' && item.checked && item.value !== '')
  const currentIdAttr = currentFirst.attrs.find(item => item.name === 'id' && item.checked && item.value !== '')
  if (preIdAttr && currentIdAttr) {
    return preIdAttr.value === currentIdAttr.value
  }
  else {
    return false
  }
}
