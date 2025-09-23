import { cloneDeep } from 'lodash-es'

import type { ASTNode } from '@/ast/ASTNode'
import type { ProcessNodeVM } from '@/corobot'
import type { ArgumentValue, NodeArgument, ProcessNode } from '@/corobot/type'
import { useProcessStore } from '@/stores/useProcessStore'
import { requiredItem } from '@/views/Arrange/components/flow/hooks/useValidate'
import { CONVERT_MAP, Else, ElseIf, LOOP_END_MAP, Module, Process } from '@/views/Arrange/config/atomKeyMap'
import { pickProcessAndModuleOptions } from '@/views/Arrange/utils'
import { exceptionKeys } from '@/views/Arrange/utils/generateData'

export function processNodeToList(astNodeList: Map<string, ASTNode>, node: ProcessNodeVM[] | RPA.Atom[], projectDoc, processId: string): RPA.Atom[] {
  const start = projectDoc.loadNumber * (projectDoc.nodeAbilityMap[processId].currentPage - 2)
  const end = projectDoc.loadNumber * (projectDoc.nodeAbilityMap[processId].currentPage - 1)
  const first = start < 0 ? 0 : start
  const last = end > 0 ? end : node.length
  for (let index = first; index < last; index++) {
    const n = node[index]
    if (!n)
      break
    const nodeItem = astNodeList.get(n.id)
    const nodeAbility = projectDoc.nodeAbility[`${n.key}***${n.version}`]
    if (!nodeItem || !nodeAbility)
      break
    const gNode = createSingleNode(n, nodeItem, nodeAbility)
    node[index] = gNode
  }
  return node.slice(start < 0 ? 0 : start, end > 0 ? end : node.length)
}

export function createSingleNode(node: ProcessNodeVM, astNode: ASTNode, nodeAbility) {
  const advanced = []
  const inputForm = []
  const outputForm = []
  nodeAbility.inputList?.forEach((item) => {
    if (item.level === 'advanced') {
      const findItem = node.advanced.find(n => n.key === item.key)
      if (findItem)
        advanced.push({ ...item, ...findItem })
    }
    else {
      const findItem = node.inputList.find(n => n.key === item.key)
      if (findItem)
        inputForm.push({ ...item, ...findItem })
    }
  })
  const commonAdvanced = cloneDeep(useProcessStore().commonAdvancedParameter).filter(item => !exceptionKeys.includes(item.key))
  commonAdvanced.forEach((advance) => {
    const findItem = node.advanced.find(n => n.key === advance.key)
    if (findItem)
      advanced.push({ ...advance, ...findItem })
  })
  nodeAbility.outputList?.forEach((item, idx) => {
    const findItem = node.outputList[idx]
    outputForm.push({ ...item, ...findItem })
  })
  if ([Process, Module].includes(node.key)) {
    for (const item of inputForm as RPA.AtomDisplayItem[]) {
      item.options = pickProcessAndModuleOptions(item)
    }
  }
  const obj: RPA.Atom = {
    ...nodeAbility,
    exception: node.exception,
    advanced,
    alias: node.alias,
    inputList: inputForm,
    outputList: outputForm,
    id: node.id,
    level: astNode?.level,
  }
  if (node.disabled)
    obj.disabled = node.disabled
  if (node.breakpoint)
    obj.breakpoint = node.breakpoint
  obj.nodeError = requiredItem(obj)
  if (astNode?.raw?.error)
    obj.nodeError = [...obj.nodeError, astNode.raw.error]
  if (Object.keys(LOOP_END_MAP).concat([ElseIf, Else]).includes(node.key)) {
    obj.isOpen = true
    obj.hasFold = true
  }
  return obj
}

export function processNodeToASTProcessNode(node: ProcessNodeVM | ProcessNodeVM[]): any {
  const arr = Array.isArray(node) ? node : [node]
  return arr.map((n) => {
    const type = CONVERT_MAP[n.key] ? CONVERT_MAP[n.key] : 'action'
    return {
      id: n.id,
      type,
    }
  })
}

export function shapeUIData(node: RPA.Atom) {
  const { inputList, outputList, advanced, exception, key, version, id, alias, disabled, breakpoint } = node
  const generateForm = (itemArr: RPA.AtomDisplayItem[]) => itemArr.map((i: RPA.AtomDisplayItem) => {
    const val = []
    const simple: NodeArgument = { key: i.key, value: '' }
    if (Array.isArray(i.value)) {
      i.value.forEach((v) => {
        let userVal: ArgumentValue = { type: v.type, value: v.value }
        if (v.data)
          userVal.data = v.data
        if (v.varId) {
          userVal = { ...v }
        }
        val.push(userVal)
      })
      simple.value = val
    }
    else {
      simple.value = i.value
    }
    if (i.show !== undefined)
      simple.show = i.show
    return simple
  })
  const obj: ProcessNode = { key, version, id, alias, inputList: generateForm(inputList), outputList: generateForm(outputList), advanced: generateForm(advanced), exception: generateForm(exception) }
  if (disabled)
    obj.disabled = disabled
  if (breakpoint)
    obj.breakpoint = breakpoint
  return obj
}
