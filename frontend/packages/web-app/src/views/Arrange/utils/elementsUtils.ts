/** @format */

import { generateUUID } from '@/utils/common'

import type { CustomValueType, DirectoryAttrItem, DirectoryItem, EleVariableType, VarDataType, WebElementType } from '@/types/resource'
import { PATTERN_RULES, PATTERN_RULES_TYPE, PATTERN_RULES_UIA } from '@/views/Arrange/config/pick'

export type ElementT = 'uia' | 'web' | 'cv' | 'jab' | 'sap'

/**
 *  元素信息格式化转换
 * @param version - version of the format
 * @param type - type of the format
 * @param data - data to format
 * @returns - formatted data
 */
export function elementDirectoryFormat(version: string = '1', type: ElementT, data: any) {
  const vFns = {
    1: elementDirectoryFormatV1,
  }
  return vFns[version](type, data)
}
/**
 * 元素信息格式化恢复
 * @param version 版本
 * @param type 类型
 * @param data 数据
 * @returns 原数据格式
 */
export function elementDirectoryFormatRecover(version: string = '1', type: ElementT, data: any) {
  const vFns = {
    1: elementDirectoryFormatV1Recover,
  }
  return vFns[version](type, data)
}

// 可视化编辑数据 v1
function elementDirectoryFormatV1(type: ElementT, data: any) {
  const tFns = {
    uia: elementDirectoryFormatV1Uia,
    web: elementDirectoryFormatV1Web,
    jab: elementDirectoryFormatV1Jab,
  }
  if (tFns[type] === undefined) { // 如果没有对应的处理函数，返回通用处理
    return elementDirectoryFormatV1Common(data, 'v1', type)
  }
  return tFns[type] && tFns[type](data)
}
// 可视化编辑数据 v1 恢复
function elementDirectoryFormatV1Recover(type: ElementT, data: any) {
  const tFns = {
    uia: elementDirectoryFormatV1UiaRecover,
    web: elementDirectoryFormatV1WebRecover,
    jab: elementDirectoryFormatV1JabRecover,
  }
  if (tFns[type] === undefined) { // 如果没有对应的处理函数，返回通用处理
    return elementDirectoryFormatV1RecoverCommon(data)
  }
  return tFns[type] && tFns[type](data)
}
// 公共格式化函数
function elementDirectoryFormatV1Common(
  data: any,
  version: string,
  typesPatternType: string,
) {
  if (!data)
    return []
  const ignoreKeys = ['checked', 'tag_name', 'disable_keys']
  return data.map((item: DirectoryItem) => {
    const attrKeys = Object.keys(item).filter(key => !ignoreKeys.includes(key))
    return {
      _version: version,
      _checkDisabled: false,
      _addDisabled: false,
      _deleteDisabled: false,
      tag: item.tag_name,
      checked: item.checked !== false,
      value: item.tag_name,
      attrs: attrKeys.map((key, index) => {
        const attr = {
          _checkDisabled: false,
          _addDisabled: false,
          _deleteDisabled: false,
          _typeDisabled: false,
          _nameDisabled: false,
          _typesPattern: typesPattern(typesPatternType, key),
          value: item[key],
          type: 0,
          name: key,
          checked: item.disable_keys ? !item.disable_keys.includes(key) : true,
          variableValue: null,
        }
        attr.variableValue = variableFormatValue(attr, index)
        return attr
      }),
    }
  })
}

// 公共恢复函数
function elementDirectoryFormatV1RecoverCommon(data: any) {
  if (!data)
    return []
  return data.map((item: any) => {
    const attrs = item.attrs
    const attrObj: any = {
      tag_name: item.value,
      checked: item.checked,
      disable_keys: [],
    }
    attrs.forEach((attr: any) => {
      const variableValue = attr.variableValue
        ? varibaleValueFormatSave(attr.variableValue.value)
        : attr.value
      attrObj[attr.name] = variableValue
      if (!attr.checked) {
        attrObj.disable_keys.push(attr.name)
      }
    })
    return attrObj
  })
}

// 可视化编辑数据 v1 uia
function elementDirectoryFormatV1Uia(data: any) {
  return elementDirectoryFormatV1Common(data, 'uia_1', 'uia_1')
}
// 可视化编辑数据 v1 uia 恢复
function elementDirectoryFormatV1UiaRecover(data: DirectoryItem[]) {
  return elementDirectoryFormatV1RecoverCommon(data)
}
// 可视化编辑数据 v1 jab
function elementDirectoryFormatV1Jab(data: any) {
  return elementDirectoryFormatV1Common(data, 'jab_1', 'jab_1')
}
// 可视化编辑数据 v1 jab 恢复
function elementDirectoryFormatV1JabRecover(data: any) {
  return elementDirectoryFormatV1RecoverCommon(data)
}
// 可视化编辑数据 v1 web
function elementDirectoryFormatV1Web(data: { pathDirs: DirectoryItem[] }) {
  if (!data || !data.pathDirs)
    return []
  return data.pathDirs.map((item: DirectoryItem) => {
    return {
      _version: 'web_1', // 版本
      _checkDisabled: item.tag === '$shadow$', // 是否禁用勾选
      _addDisabled: false, // 是否禁用添加
      _deleteDisabled: item.tag === '$shadow$', // false, // 是否禁用删除
      tag: item.value || item.tag,
      checked: item.checked === true,
      value: item.value || item.tag,
      attrs: item.attrs.map((attr: DirectoryAttrItem, index: number) => {
        return {
          variableValue: variableFormatValue(attr, index),
          // _checkDisabled: true, // 是否禁用勾选
          // _addDisabled: true, // 是否禁用添加
          _deleteDisabled: true, // 是否禁用删除
          // _typeDisabled: true, // 是否禁用类型修改
          _nameDisabled: true, // 是否禁用名称修改
          _typesPattern: typesPattern('web_1', attr.name),
          value: attr.value,
          type: attr.type || 0,
          name: attr.name,
          checked: attr.checked === true,
        }
      }),
    }
  })
}
// 可视化编辑数据 v1 web 恢复
function elementDirectoryFormatV1WebRecover(data: DirectoryItem[]) {
  if (!data)
    return []
  return data.map((item: DirectoryItem) => {
    return {
      tag: item.value || item.tag,
      checked: item.checked,
      value: item.value,
      attrs: item.attrs.map((attr: DirectoryAttrItem & { variableValue: EleVariableType }) => {
        const variableValue = attr.variableValue ? varibaleValueFormatSave(attr.variableValue.value) : attr.value
        return {
          name: attr.name,
          value: variableValue,
          checked: attr.checked,
          type: attr.type,
        }
      }),
    }
  })
}
// 匹配规则， uia 只有等于， web后续要支持多种
export function typesPattern(type: string, name: string) {
  const tpMap = {
    uia_1: PATTERN_RULES_UIA,
    web_1: PATTERN_RULES,
    jab_1: PATTERN_RULES_UIA,
  }
  const rules = tpMap[type] || []
  if (name === 'index') {
    // index 类型为数字 只有等于条件
    return rules.filter(item => item.value === 0)
  }
  return rules.length > 0 ? rules : PATTERN_RULES_UIA // 如果没有对应的规则，则使用默认规则
}

/**
 *  返回attrs 选中的属性
 */
export function checkedValue(tag: string, attrs: any[]) {
  //
  let str = ''
  str += `<${tag}`
  attrs.forEach((item) => {
    if (item.checked) {
      str += ` ${item.name}${PATTERN_RULES_TYPE[item.type]}"${item.value}"`
    }
  })
  str += ` />`
  return str
}
/**
 * custom 自定义编辑的数据格式化
 * @param version 版本
 * @param type 类型
 * @param data 原数据
 * @returns 新数据
 */
export function elementCustomFormat(version: string = '1', type: ElementT, data: any) {
  const vFns = {
    1: elementCustomFormatV1,
  }
  return vFns[version](type, data)
}
// 自定义编辑数据 恢复
export function elementCustomFormatRecover(version: string = '1', type: ElementT, data: any) {
  if (!data)
    return {}
  const vFns = {
    1: elementCustomFormatV1Recover,
  }
  return vFns[version](type, data)
}

/**
 * 自定义编辑数据格式化，v1 版本
 */
function elementCustomFormatV1(type: ElementT, data: any) {
  const tFns = {
    // uia: null, // 无需处理
    web: elementCustomFormatV1Web,
  }
  return tFns[type] && tFns[type](data)
}
// 自定义编辑数据 v1 web 格式化
function elementCustomFormatV1Web(data: WebElementType) {
  if (!data)
    return []
  const { xpath, cssSelector, shadowRoot, url, isFrame, iframeXpath } = data
  const resArr = [
    {
      name: 'url',
      value: url,
    },
    {
      name: 'xpath',
      value: xpath,
    },
    {
      name: 'cssSelector',
      value: cssSelector,
    },
  ]
  if (shadowRoot) {
    // shadowRoot 使用 cssSelector 匹配，不使用 xpath
    // 删掉 xpath 那一项
    const xapthIndex = resArr.findIndex(item => item.name === 'xpath')
    resArr.splice(xapthIndex, 1)
  }
  if (isFrame) {
    const urlIndex = resArr.findIndex(item => item.name === 'url')
    resArr.splice(urlIndex, 1) // 删除 url
    resArr.unshift({
      name: 'iframeXpath',
      value: iframeXpath,
    })
  }
  const res = customValueFormatVariable(resArr)
  return res
}
// 自定义编辑数据 恢复
function elementCustomFormatV1Recover(type: ElementT, data: any) {
  const tFns = {
    // uia: elementCustomFormatV1Uia,
    web: elementCustomFormatV1WebRecover,
  }
  return tFns[type] && tFns[type](data)
}
// 自定义编辑数据 web 恢复
function elementCustomFormatV1WebRecover(data: any[]) {
  const obj = {}
  data.forEach((item) => {
    const variableObj = varibaleValueFormatSave(item.value)
    obj[item.name] = variableObj
  })
  return obj
}

/**
 * 将数组数据格式化为 支持变量的模式数据
 */
function customValueFormatVariable(arr: CustomValueType[]) {
  return arr.map((item, index) => {
    return variableFormatValue(item, index)
  })
}
// 将数据格式化为 支持变量的模式数据
// "xpath": {
//   "rpa": "special",
//   "value": [
//       {
//           "type": "var",
//           "value": "var1"
//       },
//       {
//           "type": "other",
//           "value": "//div[@id='test']"
//       }
//   ]
// }
function variableFormatValue(item: DirectoryAttrItem | CustomValueType, index: number) {
  const variableValue = makeVaribaleValue(item.value) // 转化成支持变量的格式
  return {
    types: 'Any',
    default: '',
    rowIdx: index,
    formType: {
      type: 'INPUT_VARIABLE',
      params: {
        values: [],
      },
    },
    key: item.name,
    title: item.name,
    name: item.name,
    value: variableValue,
    show: true,
    uniqueKey: generateUUID(),
  }
}

/**
 * 制作变量
 */
function makeVaribaleValue(val: EleVariableType | any) {
  // 判断 val 是否是 {rpa: 'special'} 格式的对象
  const isVariable = val !== null
    && typeof val === 'object'
    && 'rpa' in val
    && val.rpa === 'special'
  const variableValue = isVariable
    ? val.value
    : [
        { type: 'other', value: val === null ? '' : val },
      ] // 转化成支持变量的格式
  return variableValue
}
/**
 * 存储变量时格式化
 */
function varibaleValueFormatSave(value: VarDataType[]) {
  return {
    rpa: 'special',
    value,
  }
}

export function addAttr(v: string, index: number) {
  const attr = {
    name: '',
    type: 0,
    value: '',
    checked: false,
    _typesPattern: typesPattern(v, ''),
    variableValue: null,
  }
  attr.variableValue = variableFormatValue(attr, index)
  return attr
}

export function addNode(v: string, originNode: DirectoryItem) {
  const node = {
    _version: v,
    tag: originNode.tag,
    checked: true,
    value: originNode.value,
    attrs: [],
  }
  return node
}

// elementAction 过滤， 过滤规则是如果more的menus中的每一项都在外层，则过滤掉外层在menus中的数据，如果more中只有一项，且外层包含，则过滤掉more
export function filterActionData(data, actions) {
  const actionData = data.filter(i => actions.includes(i.key) || i.menus.some(item => actions.includes(item.key))).map((i) => {
    if (i.menus) {
      i.menus = i.menus.filter(item => actions.includes(item.key))
    }
    return i
  })
  const moreItem = actionData.find(item => item.key === 'more')
  if (!moreItem)
    return actionData

  const moreMenusKeys = moreItem.menus.map(item => item.key)
  const externalItems = actionData.filter(item => item.key !== 'more')

  // 如果more中只有一项，且外层包含，则过滤掉more
  if (moreItem.menus.length === 1 && externalItems.some(extItem => extItem.key === moreItem.menus[0].key)) {
    return actionData.filter(item => item.key !== 'more')
  }

  // 检查more中的menus是否都在外层
  // const allInMore = moreMenusKeys.every(key => externalItems.some(extItem => extItem.key === key));

  // 如果more中的每一项都在外层，则过滤掉外层在menus中的数据
  // if (allInMore) {
  return actionData.filter(item => item.key === 'more' || !moreMenusKeys.includes(item.key))
  // }

  // return actionData;
}
