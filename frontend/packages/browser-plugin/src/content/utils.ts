import { StatusCode } from './constant'
import { InputTypeMap, TagMap } from './tag'

export const Utils = {
  removeUrlParams(url: string) {
    return url.replace(/\?.*$/, '')
  },

  isNumberStartString(str: string) {
    return /^\d/.test(str)
  },

  isNumberString(str: string) {
    return /\d/.test(str)
  },

  isSpecialCharacter(str: string) {
    if (this.isNumberStartString(str))
      return true
    if (/[·~`!@#$%^&*()+={}\\[\]|:;"'<>,.?/（）￥！、；：“”‘’【】《》，。？—]/.test(str))
      return true
    return false
  },

  isSupportUrl(str: string) {
    return /^(http|https|ftp|file):\/\/.+$/.test(str)
  },

  getTag(element: HTMLElement) {
    const tag = element.tagName.toLowerCase()
    if (tag === 'input') {
      const type = element.getAttribute('type')
      if (InputTypeMap[type])
        return InputTypeMap[type]
      else return '输入框'
    }
    else if (TagMap[tag]) {
      return TagMap[tag]
    }
    else {
      return '其他元素'
    }
  },

  isDynamicAttribute(attrName: string, attrValue: string) {
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
    const longRandomPattern = /^[\w-]{20,}$/
    const dynamicKeywords = ['session-', 'token-', 'uuid-', 'id-', 'key-', 'time-', 'rand-']
    const lowerValue = attrValue.toLowerCase()

    if (attrName === 'id') {
      return uuidPattern.test(attrValue) || longRandomPattern.test(attrValue) || dynamicKeywords.some(kw => lowerValue.includes(kw))
    }
    return dynamicKeywords.some(kw => lowerValue.includes(kw))
  },

  isControlCharacter(str: string) {
    return /[\x00-\x1F\x7F]/.test(str)
  },

  isEffectCharacter(str: string) {
    return /[a-z\u4E00-\u9FA5]/i.test(str)
  },

  isSpaceCharacter(str: string) {
    return /^\s.*|\s$/.test(str)
  },

  pureText(str: string) {
    str.replaceAll(/[\x00-\x1F\x7F]/g, '')
    if (str.startsWith(' ')) {
      str = str.replace(/^\s+/, '')
    }
    if (str.endsWith(' ')) {
      str = str.replace(/\s+$/, '')
    }
    return str
  },

  generateColumnNames(num: number) {
    let result = ''
    while (num > 0) {
      const remainder = (num - 1) % 26
      const char = String.fromCharCode(65 + remainder)
      result = char + result
      num = Math.floor((num - 1) / 26)
    }
    return result
  },

  generateColor(index: number) {
    const colors = [
      '#FF5733',
      '#33FF57',
      '#3357FF',
      '#FF33A1',
      '#A133FF',
      '#33FFF5',
      '#F5FF33',
      '#FF3333',
      '#33FFA1',
      '#8A33FF',
    ]
    return colors[index % colors.length]
  },

  generateRandomColor() {
    const r = Math.floor(Math.random() * 256)
    const g = Math.floor(Math.random() * 151) + 50
    const b = Math.floor(Math.random() * 256)
    return `rgb(${r},${g},${b})`
  },

  pureObject(obj: object, keys = []) {
    for (const key in obj) {
      if (!keys.includes(key)) {
        delete obj[key]
      }
    }
    return obj
  },

  success(data, msg = 'success') {
    return {
      code: StatusCode.SUCCESS,
      data,
      msg,
    }
  },

  fail(msg = 'failed', code = StatusCode.UNKNOWN_ERROR) {
    return {
      data: null,
      code,
      msg,
    }
  },

  result(data, msg = 'success', code = StatusCode.SUCCESS) {
    return {
      code,
      data,
      msg,
    }
  },
}
