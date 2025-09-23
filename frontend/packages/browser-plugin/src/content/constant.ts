export const MAX_TEXT_LENGTH = 7
export const DEEP_SEARCH_TRIGGER = 5 * 1000
export const ELEMENT_SEARCH_TRIGGER = 200
export const SCROLL_TIMES = 20
export const SCROLL_DELAY = 1500
export const HIGHT_BOX_SHADOW = 'inset 0px 0px 0px 2px red;'
export const HIGH_LIGHT_BG = '#ff4d4f85'
export const HIGH_LIGHT_BORDER = '2px solid red'
export const HIGH_LIGHT_COLOR = 'red'
export const HIGH_LIGHT_DURATION = 3000
export enum StatusCode {
  SUCCESS = '0000',
  UNKNOWN_ERROR = '5001',
  ELEMENT_NOT_FOUND = '5002',
  EXECUTE_ERROR = '5003',
  VERSION_ERROR = '5004',
}

export enum ErrorMessage {
  ELEMENT_INFO_INCOMPLETE = '元素信息不完整，无法定位元素',
  ELEMENT_NOT_FOUND = '元素未找到',
  ELEMENT_MULTI_FOUND = '找到多个元素，无法唯一定位',
  ELEMENT_NOT_INPUT = '该元素不是原生输入元素',
  ELEMENT_NOT_CHECKED = '元素无选中属性',
  ELEMENT_NOT_SELECT = '该元素不是原生选框元素',
  UNSUPPORT_ERROR = '暂不支持',
}

export const SVG_NODETAGS = [
  'svg',
  'g',
  'defs',
  'symbol',
  'use',
  'image',
  'switch',
  'a',
  'text',
  'tspan',
  'textPath',
  'foreignObject',
  'rect',
  'circle',
  'ellipse',
  'line',
  'polyline',
  'polygon',
  'path',
  'animate',
  'animateMotion',
  'animateTransform',
  'set',
  'linearGradient',
  'radialGradient',
  'pattern',
  'clipPath',
  'mask',
  'filter',
  'feBlend',
  'feColorMatrix',
  'feComponentTransfer',
  'feComposite',
  'feConvolveMatrix',
  'feDiffuseLighting',
  'feDisplacementMap',
  'feFlood',
  'feGaussianBlur',
  'feImage',
  'feMerge',
  'feMorphology',
  'feOffset',
  'feSpecularLighting',
  'feTile',
  'feTurbulence',
  'feDistantLight',
  'fePointLight',
  'feSpotLight',
  'marker',
  'view',
  'metadata',
  'title',
  'desc',
]
