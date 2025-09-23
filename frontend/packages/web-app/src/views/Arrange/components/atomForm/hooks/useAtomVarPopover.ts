import { ATOM_FORM_TYPE } from '@/constants/atom'
import useCursorStore from '@/stores/useCursorStore'
import { useProcessStore } from '@/stores/useProcessStore'
import { generateHtmlVal } from '@/views/Arrange/components/atomForm/hooks/useRenderFormType'
import { ORIGIN_SPECIAL, ORIGIN_VAR, SINGLE_VAR_TYPE_ARR } from '@/views/Arrange/config/atom'
import type { FlowVariable, GlobalVariable, VariableFunction } from '@/views/Arrange/types/variable'

import type { VarTreeItem } from '../../../types/flow'
import { transDataForPreview } from '../../customDialog/utils'

const outputStrType = [
  { label: ATOM_FORM_TYPE.COLOR },
  { label: ATOM_FORM_TYPE.DATETIME },
  { label: ATOM_FORM_TYPE.FILE },
  { label: ATOM_FORM_TYPE.TEXTAREAMODAL },
  { label: ATOM_FORM_TYPE.CONTENTPASTE },
]

export function createDom(inputVal: any, renderData: RPA.AtomDisplayItem, origin: string) {
  const cursorStore = useCursorStore()
  const { val } = inputVal
  const { formType: { type }, key, isExpr } = renderData
  const typeArr = type.split('_')
  const editableDiv: HTMLDivElement = document.querySelector(`#rpa_input_${key}`)
  const find = outputStrType.find(item => typeArr.includes(item.label))
  if (!editableDiv)
    return

  let hrElement = null
  if (isExpr) {
    // 如果是py模式那直接输出字符串
    hrElement = creaetTextNode(val)
  }
  else if (Object.is(type, ATOM_FORM_TYPE.RESULT)) {
    // 如果是输出结果，则直接输出字符串且只能输出一个变量
    setEditTextContent(key, val)
  }
  else if ((find && origin !== ORIGIN_VAR) || origin === ORIGIN_SPECIAL) {
    // 如果来源是对应按钮icon，则直接输出字符串
    editableDiv.innerHTML = ''
    hrElement = creaetTextNode(val)
  }
  else if (isSingleVar(key)) {
    // 如果是浏览器对象，excel对象，word对象，则只能输出一个变量
    editableDiv.innerHTML = ''
    hrElement = creaetHr(val, inputVal)
  }
  else if (Object.is(type, ATOM_FORM_TYPE.PICK) || Object.is(type, ATOM_FORM_TYPE.CVPICK)) {
    // 如果是pick类型，则直接输出hr标签
    editableDiv.innerHTML = ''
    hrElement = creaetHr(val, inputVal)
  }
  else {
    hrElement = creaetHr(val, inputVal)
  }
  hrElement && cursorStore.setCursorPos(hrElement, editableDiv)
  generateHtmlVal(editableDiv, renderData)
  return true
}

function creaetTextNode(val: string) {
  return document.createTextNode(val)
}

function creaetHr(val: string, inputVal: any) {
  const { elementId, category } = inputVal
  let hrElement = null
  hrElement = document.createElement('hr')
  hrElement.className = 'ui-at'
  hrElement.setAttribute('data-name', val)
  if (elementId)
    hrElement.setAttribute('data-id', elementId)
  if (category)
    hrElement.setAttribute('data-category', category)
  return hrElement
}

export function setEditTextContent(id: string, text: string) {
  const editableDiv = document.querySelector(`#rpa_input_${id}`)
  editableDiv.innerHTML = text
}

function getDialogResultFuncList(item) {
  const formModelObj = transDataForPreview(JSON.parse(item?.dialogResult || '{}')?.value)?.formModel

  return Object.keys(formModelObj ?? {}).map((keyItem: string) => ({
    key: `DialogResult.${keyItem}`,
    funcDesc: keyItem,
    resType: Array.isArray(formModelObj[keyItem]) ? 'List' : 'Str',
    resDesc: Array.isArray(formModelObj[keyItem]) ? '列表' : '字符串',
    useSrc: `@{self:self}.${keyItem}`,
  }))
}

export function generateValTree(treeArr: Array<FlowVariable & GlobalVariable & { definition?: string, atomId?: string, template?: string }>): VarTreeItem[] {
  const processStore = useProcessStore()

  return treeArr.map((item, index) => {
    const { value, types, globalId, varName, varType, atomId } = item
    const { desc, funcList, key } = processStore.globalVarTypeList[types || varType]

    const titelName = Array.isArray(value) ? value.map(it => it.value).join('') : varName
    const finalFuncList = types === 'DialogResult' ? getDialogResultFuncList(item) : funcList // 针对DialogResult类型动态生成funcList

    return {
      title: `${titelName} (${desc})`,
      key: `${key}${index}`,
      id: globalId || atomId,
      definition: item.definition,
      template: item.template,
      children: finalFuncList.map((fn: VariableFunction) => ({
        title: `${fn.funcDesc} (${fn.resDesc})`,
        key: `${titelName}/${fn.useSrc}`,
        isLeaf: true,
      })),
    }
  })
}

// 去重
export function varListUnique(arr: any[]) {
  const seenValues = new Set()
  const uniqueData = arr.filter((item) => {
    const isUnique = item.value.some(v => !seenValues.has(v.value))
    item.value.forEach(v => seenValues.add(v.value))
    return isUnique
  })
  return uniqueData
}

// 是否只能输入一个变量
export function isSingleVar(type: string) {
  return SINGLE_VAR_TYPE_ARR.includes(type)
}

function useAtomVarPopover() { }

export default useAtomVarPopover
