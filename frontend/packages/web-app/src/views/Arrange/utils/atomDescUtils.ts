/** @format */

import { isArray } from 'lodash-es'

import { CONDITION_OPTIONS_DATAFRAME_TYPE, CONDITION_OPTIONS_EXCEL_TYPE, defaultValueText, SPECIALKEY } from '@/views/Arrange/config/flow'
import { varHtmlToStr } from '@/views/Arrange/utils/index'

export function replaceStrFunc(str, replaceStr, key, value, placeholder, inputList) {
  const specialKey = `${SPECIALKEY + key + SPECIALKEY}`
  if (key === 'logic_text' && value && value.length) {
    if (isArray(value)) {
      const logicStr = value
        .map((i, idx) => {
          let res
          const targetConditionButton = inputList.find(it => it.key === key)
          // return `***#####（${i.conditionalValue} ${i.logic} ${i.reducedValue}）***#####${idx === (value.length - 1) ? '***' : item.inputLogicOperator}`
          // 遇到包含和不包含前后要对调
          if (i.logic === 'in' || i.logic === 'notIn') {
            res = `${i.reducedValue} ${i.logic} ${i.conditionalValue}`
          }
          else if (i.logic === '!') {
            res = `${i.logic} ${i.conditionalValue}`
          }
          else if (i.logic === 'notNull') {
            res = `${i.conditionalValue} != null`
          }
          else if (i.logic === 'null') {
            res = `${i.conditionalValue} == null`
          }
          else if (i.logic === 'true') {
            res = `${i.conditionalValue} == true`
          }
          else if (i.logic === 'false') {
            res = `${i.conditionalValue} == false`
          }
          else {
            const specialItem = CONDITION_OPTIONS_DATAFRAME_TYPE.find(cItem => cItem.operator === i.logic)
            if (i.sort && !i.childCondition) {
              res = `筛选列号为${i.sort}的值${specialItem?.label}${i.conditionalValue}`
            }
            else if (i.sort && i.childCondition) {
              const tips = i.childCondition.map((child) => {
                const condition = []
                if (child.conditionValue !== '' && child.conditionValue !== defaultValueText) {
                  varHtmlToStr(child.conditionValue)?.forEach((conditionItem) => {
                    condition.push(conditionItem.value)
                  })
                }
                const specialItemExcel = CONDITION_OPTIONS_EXCEL_TYPE.find(option => option.operator === child.expression)
                return `筛选列号为${i.sort}的值${specialItemExcel?.label}${condition.join(' ')}`
              })
              res = `${tips.join()}`
            }
            else {
              res = `${i.conditionalValue} ${i.logic} ${i.reducedValue}`
            }
          }
          return `***#####${specialKey}（${res}）***#####${idx === value.length - 1 ? '***' : specialKey + targetConditionButton.inputLogicOperator}`
        })
        .join()
      return str.replaceAll(`(${replaceStr})`, logicStr)
    }
  }
  if (isArray(value)) {
    const des = getValue(value)
    return str.replaceAll(replaceStr, `***#####${specialKey}${(value.length ? des : '') || placeholder}***`)
  }
  if (key === 'url') {
    const specialItem = inputList.find(data => data.key === 'url')
    if (specialItem && specialItem.formType === 'INPUT_SELECT') {
      const selectValue = specialItem?.selectValue
      const valueArray = varHtmlToStr(value)
      const des = getValue(valueArray)
      return str.replaceAll(!placeholder && !value ? `(${replaceStr})` : replaceStr, `***#####${specialKey}${selectValue}${des}***`)
    }
  }
  return str.replaceAll(!placeholder && !value ? `(${replaceStr})` : replaceStr, `***#####${specialKey}${value || placeholder}***`)
}

// 展示
export function getValue(value = []) {
  return value.map(i => i.value).join('')
}

export function setStyle() {
  const timer = setTimeout(() => {
    clearTimeout(timer)
    let elements = document.getElementsByClassName('tags-suffix')
    if (elements && elements.length > 0 && elements[0].children.length === 2) {
      const elementFirst = elements[0] as HTMLElement
      elementFirst.style.setProperty('width', '40px', 'important')
      let inputEditor = document.getElementsByClassName('rpa-wangEditor')[0]
      if (inputEditor) {
        inputEditor[0].style.setProperty('margin-right', '38px', 'important')
      }
      inputEditor = null
    }
    elements = null
  }, 0)
}

export function validateConditional({ operands, operators }, formObj) {
  const operandsResults = operands.map((item) => {
    const leftValue = formObj[item.left].value
    const rightValue = item.right
    let result = false
    try {
      switch (item.operator) {
        case '>':
          result = leftValue > rightValue
          break
        case '<':
          result = leftValue < rightValue
          break
        case '==':
          result = leftValue === rightValue
          break
        case '>=':
          result = leftValue >= rightValue
          break
        case '<=':
          result = leftValue <= rightValue
          break
        case '!=':
          result = leftValue !== rightValue
          break
        case 'in':
          result = rightValue.includes(leftValue)
          break
        default:
      }
    }
    catch {
      result = false
    }
    return result
  })

  // operators==='and' 条件全部满足，则此项展示, operators==='or' 条件部分满足，
  return operators === 'and' ? operandsResults.every(i => i) : operandsResults.some(i => i)
}
