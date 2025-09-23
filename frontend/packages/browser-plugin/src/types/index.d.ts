/** @format */
declare enum StatusCode {
  SUCCESS = '0000',
  UNKNOWN_ERROR = '5001',
  ELEMENT_NOT_FOUND = '5002',
  EXECUTE_ERROR = '5003',
  VERSION_ERROR = '5004',
}
interface ElementPosition {
  element: HTMLElement
  x: number
  y: number
  width: number
  height: number
  top: number
  left: number
  bottom: number
  right: number
}

interface ElementRange {
  start: {
    x: number
    y: number
  }
  end: {
    x: number
    y: number
  }
}

interface Point {
  x: number
  y: number
}

interface ElementDirectory {
  tag: string
  value: string
  checked: boolean
  attrs: ElementAttrs[]
}

interface ElementAttrs {
  name: string
  value: string | number
  checked: boolean
  type: number
}

interface DOMRectT {
  left: number
  top: number
  width: number
  height: number
  right: number
  bottom: number
  x: number
  y: number
}

interface ElementParams {
  key: string
  data: ElementInfo
}

interface Options {
  relativeType: 'child' | 'parent' | 'sibling'
  elementGetType: 'index' | 'xpath' | 'last' | 'all' | 'next' | 'prev' | ''
  index?: number
  xpath?: string
}

interface ElementInfo {
  xpath: string
  cssSelector: string
  pathDirs: Array<ElementDirectory>
  parentClass?: string
  rect: DOMRectT
  domain: string
  url: string
  shadowRoot: boolean
  tabTitle?: string
  tabUrl?: string
  favIconUrl?: string
  isFrame?: boolean
  checkType?: 'visualization' | 'customization'
  matchTypes?: Array<string>

  frameId?: number
  iframeXpath?: string
  iframeCssSelector?: string
  similarCount?: number
  preData?: ElementInfo
  tag?: string
  text?: string

  openSourcePage?: boolean
  value_type?: string
  batchType?: string

  index?: number
  count?: number

  relativeOptions?: Options

  atomConfig?: any
}

interface SocketParamsType {
  url?: string
  port?: number
  noCreatRouters?: Array<string>
  noInitCreat?: boolean
  reconnectMaxTime?: number
  reconnectDelay?: number
  isReconnect?: boolean
  reconnectCount?: number
  heartTime?: number
}

interface ContentResult {
  code: StatusCode
  data: any
  msg: string
}

interface FrameDetails {
  errorOccurred: boolean
  processId: number
  frameId: number
  parentFrameId: number
  url: string
  documentId: string
  parentDocumentId?: string
  documentLifecycle: chrome.extensionTypes.DocumentLifecycle
  frameType: chrome.extensionTypes.FrameType
  iframeXpath?: string
  iframeCssSelector?: string
  xpath?: string
}

interface Rects {
  x: number
  y: number
  width: number
  height: number
  left: number
  top: number
  right: number
  bottom: number
}

interface CookieDetails {
  url: string
  name?: string
  value?: string
  domain?: string
  path?: string
  secure?: boolean
  httpOnly?: boolean
  expirationDate?: number
}

interface SimilarDataValueT {
  text: string
  attrs?: {
    text?: string
    src?: string
    href?: string
  }
}

interface GenerateParamsT {
  type: 'xpath' | 'cssSelector'
  value: string
}

type XPathStep = string

interface WatchXPathResult {
  found: boolean
  lastMatchedNode: Node | null
  lastMatchedStep: XPathStep | null
  notFoundStep: XPathStep | null
  notFoundIndex?: number
}
interface CurrentFrameInfo {
  frameId?: number
  iframeXpath: string
  iframeTransform?: {
    scaleX: number
    scaleY: number
  }
}

type Strategy = 'all' | 'visualization' | 'customization'
