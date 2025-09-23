import { isEmpty } from 'lodash-es'

import i18next from '@/plugins/i18next'

import { Group, GroupEnd } from '@/views/Arrange/config/atomKeyMap'
import { DEFAULT_DESC_TEXT, SPECIALKEY } from '@/views/Arrange/config/flow'
import { backContainNodeIdx, getIdx } from '@/views/Arrange/utils/flowUtils'

import { replaceStrFunc } from './atomDescUtils'
import { caculateConditional } from './selfExecuting'

// 渲染原子能力的备注
export function renderAtomRemark(item: RPA.Atom) {
  const { key, isOpen, id, inputList, outputList, advancedItems } = item
  if (!id)
    return
  if ([Group, GroupEnd].includes(key)) {
    let desc = ''
    if (key === Group && !isOpen) {
      const startIdx = getIdx(id)
      const endIdx = backContainNodeIdx(id)
      desc = `共${endIdx - startIdx - 1}条指令`
    }
    return desc
  }
  const desc = i18next.translate(item.comment)
  const title = i18next.translate(item.alias)

  if (!desc)
    return title // 配置完成删除

  const replaceStrings = desc.match(/(?<=\{)(.+?)(?=\})/g)
  if (!replaceStrings)
    return desc

  const replaceArr = replaceStrings.map((str) => {
    const arr = str.split(':')
    return {
      key: arr[0],
      keyArr: arr[0].split('||'),
      placeholderText: arr[1] || '',
      input: false,
    }
  })

  const userFormItems = inputList.concat(outputList || []).concat(advancedItems || [])
  const userDataObj = {}
  userFormItems.forEach((i) => {
    userDataObj[i.key] = i
  })
  const formItemValues = {}
  const formItemsObj = {}
  userFormItems.forEach((i) => {
    const findItem = i
    if (!findItem)
      return
    const val = findItem.value === '""' ? '' : findItem.value
    // 根据表单类型展示不同的值  配置时需要注意此项，根据不同的情况修改此处
    if (i.options && findItem.value) {
      const withOption = i.options.find(opt => opt.value === findItem.value)
      formItemValues[i.key] = withOption ? i18next.translate(withOption.label) : val
    }
    else {
      // formItemValues[i.key] = val ? varHtmlToStr(val) : val;
      // val可能是数组，有可能是字符串，数字，undefined等
      if (Array.isArray(val)) {
        formItemValues[i.key] = (val || []).map(i => i.value).join('')
      }
      else {
        formItemValues[i.key] = val
      }
    }
    formItemsObj[i.key] = i
  })
  // 将描述信息中的变量替换为表单值
  let str = desc
  replaceArr.forEach(({ key, keyArr, placeholderText }) => {
    const specialKey = `${SPECIALKEY + key + SPECIALKEY}`
    const replaceStr = `@{${key}${placeholderText ? `:${placeholderText}` : ''}}`
    const placeholder = placeholderText === 'null' ? '' : placeholderText || DEFAULT_DESC_TEXT
    if (keyArr.length > 1) {
      // 说明此处的展示字段为多个字段中的一个, 根据conditional对应的字段进行展示
      const showKeys = keyArr.filter((k) => {
        if (!k)
          return false
        const dynamics = formItemsObj[k].dynamics
        if (isEmpty(dynamics))
          return true
        return caculateConditional(dynamics, userDataObj, formItemsObj[k])
      })
      if (showKeys.length > 0) {
        const showKey = showKeys[0]
        str = replaceStrFunc(str, replaceStr, showKey, formItemValues[showKey], placeholder, inputList)
      }
      else {
        str = str.replaceAll(!placeholder ? `(${replaceStr})` : replaceStr, `***#####${specialKey}${placeholder}***`)
      }
    }
    else {
      str = replaceStrFunc(str, replaceStr, key, formItemValues[key], placeholder, inputList)
    }
  })

  return str.split('***').map((i) => {
    if (i.includes('#####')) {
      const v = i.split('#####')
      let result = null
      if (v.length === 2) {
        const s = v[1]
        if (s.includes(SPECIALKEY)) {
          const sr = s.split(SPECIALKEY)
          const currentItem = formItemsObj[sr[1].split('||')[0]]
          result = currentItem && sr.length === 3 ? { variable: true, sr, currentItem: { ...currentItem, ...userDataObj[currentItem.key] } } : ''
          // result = sr.length === 3 ? { variable: true, sr } : ''
        }
      }
      return result || ''
    }
    return i
  })
}
