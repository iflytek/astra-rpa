import { useFlowStore } from '@/stores/useFlowStore'
import type { AnyObj } from '@/types/common'
import { Group, GroupEnd } from '@/views/Arrange/config/atomKeyMap'
import type { AtomTabs } from '@/views/Arrange/types/atomForm'
import { generateFormMap } from '@/views/Arrange/utils/generateData'
import { buildDependencyMap, checkAndExecuteDependencies, initializeExpressions } from '@/views/Arrange/utils/selfExecuting'

// 根据用户选择的节点，生成对应的配置表单
export function useBaseConfig(chooseData: RPA.Atom, t) {
  const atomData = generateFormMap(chooseData)
  const {
    inputList,
    outputList,
    id,
    key,
    baseForm,
    advanced,
    exception,
    noAdvanced, // 是否有高级配置
  } = atomData
  generateBaseForm(baseForm, key, id)
  checkConditionalShow(atomData)
  const random = Math.random()

  const atomTab: AtomTabs[] = [
    {
      key: 'baseParam',
      name: t('basicParameters'),
      params: [
        {
          name: { 'zh-CN': '基本信息', 'en-US': 'Base information' },
          key: `base${random}`,
          formItems: baseForm ?? [],
        },
        {
          name: { 'zh-CN': '输入信息', 'en-US': 'Input information' },
          key: `input${random}`,
          id: id ?? '',
          atomKey: key ?? '',
          formItems: inputList ?? [],
        },
        {
          name: { 'zh-CN': '输出信息', 'en-US': 'Output information' },
          key: `output${random}`,
          formItems: outputList ?? [],
        },
      ],
    },
    {
      key: 'advancedParam',
      name: t('advancedParameters'),
      params: [
        {
          key: `advanced${random}`,
          formItems: advanced,
        },
      ],
    },
    {
      key: 'exceptParam',
      name: t('exceptionHandling'),
      params: [
        {
          key: `exception${random}`,
          formItems: exception,
        },
      ],
    },
  ]
  atomTab[0].params = atomTab[0].params.filter(
    item => item.formItems.length > 0,
  )
  if (noAdvanced) {
    atomTab.splice(1, 3)
  }
  return atomTab
}

// 如果是编组需要特殊处理
function generateBaseForm(baseForm: RPA.AtomFormBaseForm[], key: string, id: string) {
  if (![GroupEnd, Group].includes(key))
    return

  for (const item of baseForm) {
    item.groupId = id
  }
}

let dependencyMap: Map<string, Array<{
  expression: string
  targetItem: any
  targetProp: string
}>> = new Map()

let conditionKey = ''

export function isConditionalKeys(key = '') {
  const flag = dependencyMap.has(key)
  conditionKey = key
  return flag
}

export function checkConditionalShow(chooseData: AnyObj) {
  const { inputList, outputList, advanced, exception } = chooseData
  const allItem = [inputList, outputList, advanced, exception]

  dependencyMap = buildDependencyMap(allItem)
  initializeExpressions(allItem, dependencyMap)
}

export function renderBaseConfig(configList: AtomTabs[]) {
  const flowStore = useFlowStore()
  const baseForm = configList[0]
  let inputList = []
  let outputList = []
  if (baseForm.params.length >= 2) {
    inputList = baseForm.params[1].formItems
  }
  if (baseForm.params.length === 3) {
    outputList = baseForm.params[2].formItems ?? []
  }
  const advanced = configList[1]?.params[0]?.formItems ?? []
  const exception = configList[2]?.params[0]?.formItems ?? []

  checkAndExecuteDependencies(conditionKey, [inputList, outputList, advanced, exception], () => dependencyMap)
  const idx = flowStore.simpleFlowUIData.findIndex(item => item.id === flowStore.activeAtom.id)
  flowStore.setFormItemValue('conditionalShow', { inputList, outputList, advanced, exception }, idx, false)
  return configList
}
