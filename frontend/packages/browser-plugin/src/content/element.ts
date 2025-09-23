import { MAX_TEXT_LENGTH, SVG_NODETAGS } from './constant'
import { highLight, highLightRects } from './highlight'
import { Utils } from './utils'

export function xpathEvaluateCount(xpath: string) {
  return document.evaluate(`count(${xpath})`, document, null, XPathResult.ANY_TYPE, null).numberValue
}

function getSupportTag(tagName: string) {
  if (Utils.isSpecialCharacter(tagName)) {
    return '*'
  }
  else {
    return tagName
  }
}

export function getText(element: HTMLElement) {
  if (element.tagName === 'INPUT') {
    return (element as HTMLInputElement).value || element.getAttribute('placeholder') || ''
  }
  else if (element.tagName === 'TEXTAREA') {
    return (element as HTMLTextAreaElement).value || element.getAttribute('placeholder') || ''
  }
  else if (element.tagName === 'SELECT') {
    return (element as HTMLSelectElement).value || element.getAttribute('placeholder') || ''
  }
  else if (element.tagName === 'IMG') {
    return element.getAttribute('alt') || ''
  }
  else {
    return element.textContent || element.innerText || ''
  }
}

function getNodeText(element: HTMLElement) {
  const nodeText
    = Array.from(element.childNodes)
      .filter(node => node.nodeType === Node.TEXT_NODE && node.textContent && node.textContent.trim())
      .map(node => node.textContent!.replace(/[\x00-\x1F\x7F]/g, '').trim())
      .find(text => text.length > 0) || ''
  return nodeText
}

export function textAttrFromElement(ele: HTMLElement) {
  const text = getText(ele).replace(/[\x00-\x1F\x7F]/g, '')
  const src = getAttr(ele, 'src')
  const href = getAttr(ele, 'href')
  const value: SimilarDataValueT = {
    text,
    attrs: {
      src,
      href,
      text,
    },
  }
  for (const key in value.attrs) {
    if (value.attrs[key] === null) {
      delete value.attrs[key]
    }
  }
  return value
}

export function getAttr(element: HTMLElement, attrName: string) {
  const attrMap = {
    id: element.getAttribute('id'),
    class: element.getAttribute('class'),
    name: element.getAttribute('name'),
    type: element.getAttribute('type'),
    value: (element as HTMLInputElement).value,
    href: (element as HTMLAnchorElement).href,
    src: (element as HTMLImageElement | HTMLSourceElement).src,
    title: element.title,
    text: getNodeText(element),
    readonly: String((element as HTMLInputElement).readOnly),
  }
  if (attrName in attrMap) {
    return attrMap[attrName] || ''
  }
  return element.getAttribute(attrName)
}

export function getAttrs(element: Element) {
  const attrs = {}
    ;['src', 'href', 'id', 'class', 'title', 'name'].forEach((key) => {
    const attr = element.getAttribute(key)?.replace(/[\u0000-\u001F\u007F]/g, '')
    attr && (attrs[key] = attr)
  })
  return attrs
}

export function isTable(element: HTMLElement) {
  return element.tagName.toLowerCase() === 'table' || element.closest('table') !== null
}

function getElementIndex(element: HTMLElement) {
  return element.parentElement
    ? Array.from(element.parentElement.children)
      .filter(sibling => sibling.tagName.toLowerCase() === element.tagName.toLowerCase())
      .indexOf(element) + 1
    : 0
}

function getAllElementIndex(element: HTMLElement) {
  return element.parentElement ? Array.from(element.parentElement.children).indexOf(element) + 1 : 0
}

function getElementNthIndex(element: HTMLElement) {
  if (hasSameTypeSiblings(element)) {
    return element.parentElement ? Array.from(element.parentElement.children).indexOf(element) + 1 : 0
  }
}

function getNodeNthIndex(element: HTMLElement) {
  if (element.parentNode) {
    return Array.from(element.parentNode.children).indexOf(element) + 1
  }
}

function hasSameTypeSiblings(element: HTMLElement) {
  return element.parentElement ? Array.from(element.parentElement.children).filter(sibling => sibling.tagName.toLowerCase() === element.tagName.toLowerCase()).length > 1 : false
}

function hasSiblings(element: HTMLElement) {
  return element.parentElement ? Array.from(element.parentElement.children).length > 1 : false
}

function hasSameClassSiblings(element: HTMLElement, className: string) {
  const siblings = element.parentElement ? Array.from(element.parentElement.children).filter(sibling => sibling !== element) : []
  if (siblings) {
    const hasSameClass = siblings.some(sibling => sibling.classList.contains(className))
    return hasSameClass
  }
  else {
    return false
  }
}

function pickClass(element: HTMLElement) {
  const classList = Array.from(element.classList)
  for (const cls of classList) {
    if (isLegalClass(cls) && !hasSameClassSiblings(element, cls)) {
      return cls
    }
  }
  return ''
}

export function elementFromPoint(x: number, y: number, docu: Document | ShadowRoot) {
  const element = docu.elementFromPoint(x, y)
  return element
}

function isUniqueIdFn(id: string) {
  return id && !Utils.isNumberString(id) && !Utils.isSpecialCharacter(id) && document.querySelectorAll(`#${id}`).length === 1
}

function isLegalClass(cls: string) {
  return cls && !Utils.isNumberString(cls) && !Utils.isSpecialCharacter(cls)
}
function isSvgElement(element: Element): boolean {
  return element.namespaceURI === 'http://www.w3.org/2000/svg'
}

export function getXpath(element: HTMLElement, absolute = false) {
  if (!element)
    return ''
  let xpath = ''
  while (element) {
    const id = element.id
    const isUniqueId = isUniqueIdFn(id)
    let tagName = getSupportTag(element.tagName.toLowerCase())
    let index = getElementIndex(element)
    let hasSublings = hasSameTypeSiblings(element)

    const isSvg = isSvgElement(element)
    tagName = isSvg ? `*` : tagName
    index = isSvg ? getAllElementIndex(element) : index
    hasSublings = isSvg ? hasSiblings(element) : hasSublings
    if (!absolute && isUniqueId) {
      xpath = `//${tagName}[@id="${id}"]${xpath}`
      break
    }
    else if (index > 0 && hasSublings) {
      xpath = `/${tagName}[${index}]${xpath}`
    }
    else {
      xpath = `/${tagName}${xpath}`
    }

    element = element.parentElement
    if (element && element.tagName.toLowerCase() === 'body' && !absolute) {
      xpath = `/${xpath}`
      break
    }
  }
  return xpath
}

export function getNthCssSelector(element: HTMLElement, isAbsolute = false): string {
  if (!element)
    return ''
  const selectors = []
  while (element) {
    const id = getAttr(element, 'id')
    const tagName = getSupportTag(element.tagName.toLowerCase())
    const isUniqueId = isUniqueIdFn(id)
    const index = getElementNthIndex(element)
    const hasSameSublings = hasSameTypeSiblings(element)
    const className = pickClass(element)
    if (tagName === 'html') {
      selectors.unshift(tagName)
      break
    }
    else if (!isAbsolute && isUniqueId) {
      selectors.unshift(`#${id}`)
      break
    }
    else if (!hasSameSublings) {
      selectors.unshift(tagName)
    }
    else if (className) {
      selectors.unshift(`${tagName}.${className}`)
    }
    else {
      selectors.unshift(`${tagName}:nth-child(${index})`)
    }

    element = element.parentElement
    if (element && element.tagName.toLowerCase() === 'body' && !isAbsolute) {
      return selectors.join('>')
    }
  }
  return selectors.join('>')
}

function onlyPositionXpath(xpath: string) {
  const pathArr = xpath.split('/')
  const positionArr = pathArr.map((item) => {
    const match2 = item.match(/\[@position\(\)=\d+\]/)
    if (item.includes('@position') && !match2) {
      const match3 = item.match(/@position\(\)=\d+/)
      if (match3) {
        const num = match3[0].split('=')[1]
        return item.replace(/\[.*\]/, `[@position()=${num}]`)
      }
    }
    return item
  })
  const path = positionArr.join('/')
  return path
}

function svgPathResolver(xpath: string) {
  const pathArr = xpath.split('/')
  const newPathArr = pathArr.map((item) => {
    if (!item || item === '*')
      return item
    const tagMatch = item.match(/^([^[]+)/)
    const tag = tagMatch ? tagMatch[1] : ''
    const attrMatch = item.match(/\[(.+)\]/)
    const attr = attrMatch ? attrMatch[1] : ''
    if (tag && tag !== '*') {
      if (SVG_NODETAGS && SVG_NODETAGS.includes(tag)) {
        if (attr) {
          const posMatch = attr.match(/^position\(\)\s*=\s*(\d+)$/)
          if (posMatch) {
            return `*[local-name()="${tag}" and position()=${posMatch[1]}]`
          }
          else {
            return `*[local-name()="${tag}" and ${attr}]`
          }
        }
        else {
          return `*[local-name()="${tag}"]`
        }
      }
      else {
        return item
      }
    }
    return item
  })
  const svgPath = newPathArr.filter(Boolean).join('/')
  return svgPath
}

export function getElementsByXpath(path: string, onlyPosition: boolean = false): HTMLElement[] | null {
  if (!path)
    return null
  if (onlyPosition) {
    path = onlyPositionXpath(path)
  }
  if (path.includes('/svg[') || path.includes('/svg/')) {
    path = svgPathResolver(path)
  }
  const result = document.evaluate(path, document, null, XPathResult.ANY_TYPE, null)
  let element = result.iterateNext() as HTMLElement
  const elements: HTMLElement[] = []
  while (element) {
    elements.push(element)
    element = result.iterateNext() as HTMLElement
  }
  return elements.length > 0 ? elements : null
}

export function getElementByXPath(xpath: string): HTMLElement | null {
  const element = xpath ? document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue : null
  return element as HTMLElement
}

export function getElementsByClassName(className: string): HTMLElement[] {
  const elements = document.querySelectorAll(`.${className}`)
  return Array.from(elements) as HTMLElement[]
}

export function getElementsByComposition(searchString: string): HTMLElement[] | null {
  const all = document.querySelectorAll(searchString)
  return Array.from(all) as HTMLElement[]
}

export function getElementBySelector(selector: string, onlyPosition: boolean = false): HTMLElement[] | null {
  if (!selector)
    return null
  if (onlyPosition) {
    selector = onlyPositionSelector(selector)
  }
  if (selector.includes('$shadow$')) {
    const sahdowElements = getShadowElementsBySelector(selector)
    return sahdowElements.length > 0 ? sahdowElements : null
  }
  else {
    const elements = Array.from(document.querySelectorAll(selector)) as HTMLElement[]
    return elements.length > 0 ? elements : null
  }
}
function onlyPositionSelector(selector: string) {
  const filteredSelector = selector
    .split('>')
    .map((part) => {
      if (part.includes(':nth-child')) {
        return part.substring(0, part.indexOf(':nth-child') + 13)
      }
      if (part.includes('.')) {
        return part.split('.')[0]
      }
      return part
    })
    .join('>')
  return filteredSelector
}

function queryDeepShadow(selectorLevels: string[], currentHosts: [Document | ShadowRoot] = [document]) {
  if (selectorLevels.length === 0)
    return []

  const currentSelector = selectorLevels[0]
  const remainingSelectors = selectorLevels.slice(1)
  const isLastLevel = remainingSelectors.length === 0

  const matches = []
  for (const host of currentHosts) {
    const elements = host.querySelectorAll(currentSelector)
    if (elements.length === 0)
      continue

    if (isLastLevel) {
      matches.push(...elements)
      continue
    }

    for (const el of elements) {
      if (el.shadowRoot) {
        const nestedMatches = queryDeepShadow(remainingSelectors, [el.shadowRoot])
        matches.push(...nestedMatches)
      }
    }
  }

  return matches
}

function getShadowElementsBySelector(selector: string) {
  const selectorLevels = selector.split('>$shadow$>')
  const allElements = queryDeepShadow(selectorLevels)
  return allElements
}

function getWeightedAttrs(attrs: ElementAttrs[]) {
  const idAttr = attrs.find(attr => attr.name === 'id')
  const typeAttr = attrs.find(attr => attr.name === 'type')
  const indexAttr = attrs.find(attr => attr.name === 'index')
  const textAttr = attrs.find(attr => attr.name === 'text')
  const textValue = (textAttr && textAttr.value) || ''
  const classAttr = attrs.find(attr => attr.name === 'class')
  if (idAttr) {
    attrs.forEach(attr => (attr.checked = false))
    idAttr.checked = true
    return attrs
  }
  if (textAttr && !Utils.isControlCharacter(String(textValue))) {
    textAttr.checked = true
    return attrs
  }
  if (classAttr && classAttr.checked) {
    return attrs
  }
  if (typeAttr) {
    typeAttr.checked = true
  }
  if (indexAttr && indexAttr.value) {
    indexAttr.checked = true
  }
  return attrs
}

export function getElementDirectory(element: HTMLElement, isAbsolute = false): ElementDirectory[] {
  if (!element)
    return []
  const elementDirectory = []
  while (element) {
    const id = getAttr(element, 'id')
    const isUniqueId = isUniqueIdFn(id)
    const className = pickClass(element)
    const type = getAttr(element, 'type')
    let tagName = getSupportTag(element.tagName.toLowerCase())
    let index = getElementIndex(element)
    let hasSubling = hasSameTypeSiblings(element)

    const isSvg = isSvgElement(element)
    tagName = isSvg ? `*` : tagName
    index = isSvg ? getAllElementIndex(element) : index
    hasSubling = isSvg ? hasSiblings(element) : hasSubling

    let attrs = []
    if (isUniqueIdFn(id))
      attrs.push({ name: 'id', value: id, checked: false, type: 0 })
    if (isSvg)
      attrs.push({ name: 'local-name', value: element.tagName.toLowerCase(), checked: true, type: 0 })
    if (hasSubling && index)
      attrs.push({ name: 'index', value: index, checked: false, type: 0 })
    if (type)
      attrs.push({ name: 'type', value: type, checked: false, type: 0 })
    if (className)
      attrs.push({ name: 'class', value: className, checked: false, type: 1 })
    if (elementDirectory.length === 0) {
      const text = getNodeText(element)
      if (text && text.length < MAX_TEXT_LENGTH && Utils.isEffectCharacter(text)) {
        attrs.push({ name: 'text', value: text, checked: false, type: 1 })
      }
    }

    attrs = getWeightedAttrs(attrs)
    const attributes = { tag: tagName, checked: true, value: tagName, attrs }
    elementDirectory.unshift(attributes)
    if (id && isUniqueId && !isAbsolute) {
      return elementDirectory
    }
    element = element.parentElement
    if (element && element.tagName.toLowerCase() === 'body' && !isAbsolute) {
      return elementDirectory
    }
  }
  return elementDirectory
}

function checkElementsByRegular(searchElements: HTMLElement[], elementDirectory: ElementDirectory[]) {
  const dirs = elementDirectory.filter(item => item.checked)
  const filterList = searchElements.filter((element) => {
    const allElements = []
    let currentElement = element
    let dlength = dirs.length
    let flag = true
    while (dlength > 0) {
      allElements.unshift(currentElement)
      currentElement = currentElement.parentElement
      dlength--
    }
    dirs.forEach((item, index) => {
      const attrs = item.attrs
      const regAttr = attrs.find(attr => attr.type === 2 && attr.checked)
      if (regAttr) {
        const nodeValue = String(regAttr.value).trim()
        if (nodeValue) {
          const node = allElements[index]
          if (node) {
            const value = getAttr(node, regAttr.name)
            try {
              const reg = new RegExp(nodeValue)
              if (!reg.test(value)) {
                flag = false
              }
            }
            catch (error) {
              console.error(`Invalid regular expression: ${nodeValue}`, error)
              flag = false
            }
          }
        }
      }
    })
    return flag
  })
  return filterList
}

export function directoryFindElement(elementDirectory: ElementDirectory[], onlyPosition: boolean = false) {
  let searchElements: HTMLElement[] = []
  const xpath = generateXPath(elementDirectory, onlyPosition)
  console.log('directoryFindElement generateXPath xpath: ', xpath)
  searchElements = getElementsByXpath(xpath, onlyPosition)
  if (searchElements && searchElements.length > 0) {
    searchElements = checkElementsByRegular(searchElements, elementDirectory)
    return searchElements
  }
  else {
    return null
  }
}

function textfn(val: string) {
  if (val.includes('"')) {
    return `text()=concat(${val
      .split('"')
      .map((part, index, arr) => (index < arr.length - 1 ? `"${part}", '"', ` : `"${part}"`))
      .join('')})`
  }
  return `text()="${val}"`
}

function conditionStr(attr: ElementAttrs) {
  attr.value = `${attr.value}`
  let condition: string
  if (attr.checked && attr.value) {
    switch (attr.name) {
      case 'index':
        condition = `position()=${attr.value}`
        break

      case 'innertext':
        condition
          = attr.type === 1
            ? `contains(., "${attr.value}")`
            : textfn(attr.value)
        break
      case 'text':
        condition
          = attr.type === 1
            ? `contains(., "${attr.value}")`
            : textfn(attr.value)
        break

      case 'local-name':
        condition = `local-name()="${attr.value}"`
        break

      default:
        condition
          = attr.type === 1
            ? `contains(@${attr.name}, "${attr.value}")`
            : `@${attr.name}="${attr.value}"`
        break
    }
  }

  return condition
}

export function generateXPath(dirs: ElementDirectory[], onlyPosition: boolean = false): string {
  if (dirs && dirs.length === 0) {
    return ''
  }
  if (onlyPosition) {
    dirs.forEach((item) => {
      item.attrs.forEach((attr) => {
        const attrValue = `${attr.value}`.trim()
        if (attr.name === 'index' && attrValue !== '') {
          attr.checked = true
        }
        else if (attr.name === 'id' && attrValue !== '') {
          attr.checked = true
        }
        else {
          attr.checked = false
        }
      })
    })
  }
  const xpath = dirs
    .filter(dir => dir.checked)
    .map((dir) => {
      const attrs = dir.attrs
        .filter((attr) => {
          if (attr.type === 2 && attr.value && attr.checked) {
            return false
          }
          else {
            return attr.checked
          }
        })
        .map((attr) => {
          const condition: string = conditionStr(attr)
          return condition
        })
        .join(' and ')
      return attrs ? `${dir.tag}[${attrs}]` : dir.tag
    })
    .join('/')
  if (xpath.startsWith('html')) {
    return `/${xpath}`
  }
  return `//${xpath}`
}

export function getMouseOverElement(document = window.document, position) {
  const { x, y } = position
  return document.elementFromPoint(x, y)
}

export function hasChildElement(element) {
  return element && element.children && element.children.length > 0
}

export function checkElements(elements: HTMLElement[]) {
  if (elements.length > 1) {
    const rects = elements.map(element => element.getBoundingClientRect().toJSON())
    highLightRects(rects)
  }
  else {
    const rect = elements[0].getBoundingClientRect().toJSON() // getBoundingClientRect(element);
    highLight(rect)
  }
}

export function getElementsByPosition(x: number, y: number) {
  const elements = document.elementsFromPoint(x, y)
  const positions = elements.map((element) => {
    const rect = element.getBoundingClientRect()
    return {
      element,
      ...rect.toJSON(),
    }
  })
  return positions
}

export function getAllElementsPositionInBody(body: HTMLElement | ShadowRoot = document.body): Array<ElementPosition> {
  const elements = Array.from(body.querySelectorAll('*')) as HTMLElement[]
  const visibleElements = Array.from(elements).filter(
    element =>
      element.tagName.toLowerCase() !== 'head'
      && element.tagName.toLowerCase() !== 'title'
      && element.tagName.toLowerCase() !== 'meta'
      && element.tagName.toLowerCase() !== 'script'
      && element.tagName.toLowerCase() !== 'style'
      && element.tagName.toLowerCase() !== 'link'
      && element?.style.display !== 'none'
      && element?.style.visibility !== 'hidden',
  )
  const visibleElements2 = visibleElements.filter(element => element.getBoundingClientRect().width > 0 && element.getBoundingClientRect().height > 0)
  const positions = []
  let shadowPositions = []
  visibleElements2.forEach((element) => {
    const rect = element.getBoundingClientRect()
    if (element && element.shadowRoot) {
      const shadowRoot = element.shadowRoot
      shadowPositions = getAllElementsPositionInBody(shadowRoot)
    }
    positions.push({
      element,
      ...rect.toJSON(),
    })
  })
  positions.push(...shadowPositions)
  return positions
}

export function getAllElementsPosition() {
  const elements = getAllElements()
  const positions = []
  elements.forEach((element) => {
    const rect = element.getBoundingClientRect()
    positions.push({
      element,
      ...rect,
    })
  })
  return positions
}

export function getAllElements() {
  const elements = document.querySelectorAll('*')
  return Array.from(elements)
}

/**
 * all frame include iframe and frame
 */
export function getAllFrames() {
  const iframeList = document.querySelectorAll('iframe') || []
  const frameList = document.querySelectorAll('frame') || []
  const frames = Array.from(iframeList).concat(Array.from(frameList))
  return frames
}

export function getWindowFrames() {
  const frames = getAllFrames()
  const framesList = Array.from(frames).map((frame) => {
    return {
      xpath: getXpath(frame),
      src: frame.src,
      rect: getFrameContentRect(frame),
    }
  })
  return framesList
}

export function getIFramesElements() {
  const frames = getAllFrames()
  return frames
}

export function getElementsFromPoints(a: { x: number, y: number }, b: { x: number, y: number }) {
  const elements = []
  for (let x = a.x; x <= b.x; x++) {
    for (let y = a.y; y <= b.y; y++) {
      const element = document.elementFromPoint(x, y)
      if (elements.includes(element))
        continue
      if (element) {
        elements.push(element)
      }
    }
  }
  return elements
}

export function getElementFromAllElements(elements: Array<ElementPosition>, range: ElementRange): Promise<Array<ElementPosition>> {
  return new Promise((resolve, reject) => {
    try {
      const result = elements.filter((item) => {
        const exp1 = item.x >= range.start.x && item.x <= range.end.x
        const exp2 = item.y >= range.start.y && item.y <= range.end.y
        const exp3 = item.x + item.width <= range.end.x
        const exp4 = item.y + item.height <= range.end.y

        return exp1 && exp2 && exp3 && exp4
      })
      resolve(result)
    }
    catch (error) {
      reject(error)
    }
  })
}

export function getClosestElementByPoint(target: Point) {
  const ele = elementFromPoint(target.x, target.y, document)
  const eles = document.elementsFromPoint ? getElementsByPosition(target.x, target.y) : getAllElementsPositionInBody()
  if (!eles.length)
    return ele
  const pointEles = eles.filter((item) => {
    return item.left <= target.x && item.top <= target.y && item.right >= target.x && item.bottom >= target.y
  })
  if (!pointEles.length)
    return ele
  const closestElement = pointEles.reduce((prev, curr) => {
    const prevDistance = Math.hypot(prev.left - target.x, prev.top - target.y, prev.right - target.x, prev.bottom - target.y)
    const currDistance = Math.hypot(curr.left - target.x, curr.top - target.y, curr.right - target.x, curr.bottom - target.y)
    return prevDistance <= currDistance ? prev : curr
  })
  return closestElement.element
}

export function findElementByPoint(target: Point, deep = false, docu: Document | ShadowRoot = document) {
  let ele = elementFromPoint(target.x, target.y, docu) as HTMLElement
  if (deep && docu instanceof Document) {
    ele = getClosestElementByPoint(target)
  }
  if (!ele)
    return null
  return ele
}

export function shadowRootElement(point: Point, shadowRoot: ShadowRoot, shadowPath: string = '', shadowDirs: ElementDirectory[] = []) {
  const { x, y } = point
  const ele = shadowRoot.elementFromPoint(x, y) as HTMLElement
  if (ele && ele.shadowRoot) {
    const shadowNth = `:nth-child(${getNodeNthIndex(ele)})`
    shadowPath = shadowPath ? `${shadowPath}>$shadow$>${getNthCssSelector(ele)}${shadowNth}` : `${getNthCssSelector(ele)}${shadowNth}`
    shadowDirs = shadowDirs.concat(getElementDirectory(ele))
    return shadowRootElement(point, ele.shadowRoot, shadowPath, shadowDirs)
  }
  else {
    return {
      element: ele,
      path: shadowPath,
      dirs: shadowDirs,
    }
  }
}

export function getZoom(element: HTMLElement) {
  let zoom = 1
  while (element) {
    const currentZoom = Number(window.getComputedStyle(element).zoom || 1)
    zoom *= currentZoom
    element = element.parentElement
  }
  return zoom
}

export function getPadding(element: HTMLElement) {
  const dpr = window.devicePixelRatio
  const computedStyle = window.getComputedStyle(element)
  const paddingLeft = Number.parseInt(computedStyle.paddingLeft) || 0
  const paddingTop = Number.parseInt(computedStyle.paddingTop) || 0
  const paddingRight = Number.parseInt(computedStyle.paddingRight) || 0
  const paddingBottom = Number.parseInt(computedStyle.paddingBottom) || 0
  return { paddingLeft: paddingLeft * dpr, paddingTop: paddingTop * dpr, paddingRight: paddingRight * dpr, paddingBottom: paddingBottom * dpr }
}

export function getBorder(element: HTMLElement) {
  const dpr = window.devicePixelRatio
  const computedStyle = window.getComputedStyle(element)
  const borderLeft = Number.parseInt(computedStyle.borderLeftWidth) || 0
  const borderTop = Number.parseInt(computedStyle.borderTopWidth) || 0
  const borderRight = Number.parseInt(computedStyle.borderRightWidth) || 0
  const borderBottom = Number.parseInt(computedStyle.borderBottomWidth) || 0
  return { borderLeft: borderLeft * dpr, borderTop: borderTop * dpr, borderRight: borderRight * dpr, borderBottom: borderBottom * dpr }
}

export function getBoundingClientRect(element: HTMLElement): DOMRectT {
  // @ts-expect-error  currentFrameInfo in window
  const iframeTransform = window.currentFrameInfo.iframeTransform
  const { scaleX = 1, scaleY = 1 } = iframeTransform
  const safeNum = 8
  const rect = element.getBoundingClientRect().toJSON()
  const dpr = window.devicePixelRatio
  const { left, top, width, height, right, bottom, x, y } = rect
  return {
    left: Math.round(left * scaleX * dpr),
    top: Math.round(top * scaleY * dpr),
    width: Math.round(width * scaleX * dpr) || safeNum,
    height: Math.round(height * scaleY * dpr) || safeNum,
    right: Math.round(right * scaleX * dpr),
    bottom: Math.round(bottom * scaleY * dpr),
    x: Math.round(x * scaleX * dpr),
    y: Math.round(y * scaleY * dpr),
  }
}

export function getFrameContentRect(element: HTMLElement) {
  const frameRect = getBoundingClientRect(element)
  const padding = getPadding(element)
  const border = getBorder(element)
  const frameContentRect = {
    left: frameRect.left + padding.paddingLeft + border.borderLeft,
    top: frameRect.top + padding.paddingTop + border.borderTop,
    width: frameRect.width - padding.paddingLeft - padding.paddingRight - border.borderLeft - border.borderRight,
    height: frameRect.height - padding.paddingTop - padding.paddingBottom - border.borderTop - border.borderBottom,
    right: frameRect.right - padding.paddingRight - border.borderRight,
    bottom: frameRect.bottom - padding.paddingBottom - border.borderBottom,
    x: frameRect.x + padding.paddingLeft + border.borderLeft,
    y: frameRect.y + padding.paddingTop + border.borderTop,
  }
  return frameContentRect
}

export function getIframeTransform(element: Element) {
  const style = window.getComputedStyle(element)
  const matrix = new DOMMatrix(style.transform)
  const scaleX = matrix.a
  const scaleY = matrix.d
  return {
    scaleX,
    scaleY,
  }
}

export function getElementByElementInfo(params: ElementInfo): HTMLElement[] | null {
  const { xpath, cssSelector, pathDirs, shadowRoot, checkType, matchTypes } = params
  const onlyPosition = matchTypes && matchTypes.includes('onlyPosition')
  if (shadowRoot) {
    return getElementBySelector(cssSelector, onlyPosition)
  }
  if (checkType === 'visualization') {
    return directoryFindElement(pathDirs, onlyPosition)
  }
  let eles = getElementsByXpath(xpath, onlyPosition)
  if (!eles || eles.length === 0) {
    eles = getElementBySelector(cssSelector, onlyPosition)
  }
  return eles
}

export function getChildElementByType(element: HTMLElement, params: Options): HTMLElement[] | HTMLElement | null {
  const { elementGetType } = params
  if (elementGetType === 'index') {
    return element.children[params.index || 0] as HTMLElement
  }
  if (elementGetType === 'all') {
    return Array.from(element.children) as HTMLElement[]
  }
  if (elementGetType === 'xpath') {
    return document.evaluate(`.${params.xpath}`, element, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue as HTMLElement
  }
  if (elementGetType === 'last') {
    return element.lastElementChild as HTMLElement
  }
}

export function getSiblingElementByType(element: HTMLElement, params: Options): HTMLElement[] | HTMLElement | null {
  const { elementGetType } = params
  if (elementGetType === 'all') {
    return Array.from(element.parentElement.children) as HTMLElement[]
  }
  if (elementGetType === 'prev') {
    return element.previousElementSibling as HTMLElement
  }
  if (elementGetType === 'next') {
    return element.nextElementSibling as HTMLElement
  }
}
