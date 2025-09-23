<!-- 子流程选择组件 -->
<script setup lang="ts">
import { find, fromPairs, get, isArray, isEqual } from 'lodash-es'
import { computed, ref, toRaw, watch } from 'vue'
import type { VxeGridProps } from 'vxe-table'

import VxeGrid from '@/plugins/VxeTable'

import { getConfigParams } from '@/api/atom'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore.ts'

import AtomConfig from './AtomConfig.vue'

interface ParamItemValue {
  rpa: 'special'
  value: Array<any>
}

type ParamValues = Array<{ varId: string, varName: string, varValue: ParamItemValue }>

const props = defineProps<{ renderData: RPA.AtomDisplayItem }>()
const emits = defineEmits<{ refresh: [value: ParamValues] }>()

const gridData = ref<Array<RPA.ConfigParamData & { form: RPA.AtomDisplayItem }>>([])

const flowStore = useFlowStore()
const processStore = useProcessStore()

const gridOptions: VxeGridProps<RPA.ConfigParamData> = {
  height: 160,
  size: 'mini',
  scrollY: { enabled: true },
  border: true,
  showOverflow: true,
  keepSource: true,
  round: true,
  columns: [
    { field: 'varName', title: '参数名', width: 100 },
    { field: 'varValue', title: '参数值', slots: { default: 'value_default' } },
  ],
}

const linkageKey = computed(() => {
  // 获取联动的选择子流程 id
  const linkageKey = get(props.renderData, ['formType', 'params', 'linkage'])
  // 只从输入信息中查找联动
  const targetFormValue = find(flowStore.activeAtom.inputList, { key: linkageKey })

  return targetFormValue?.value
})

watch(linkageKey, async (newLinkageKey) => {
  if (!newLinkageKey) {
    gridData.value = []
    return
  }

  const list = await getConfigParams({ robotId: processStore.project.id, processId: newLinkageKey })

  const preValues: Record<string, ParamItemValue> = fromPairs(list.map(it => ([
    it.id,
    { rpa: 'special', value: [{ type: 'other', value: it.varValue }] },
  ])))

  if (isArray(props.renderData.value)) {
    const values = props.renderData.value as unknown as ParamValues
    // 将当前流程的参数值设置到 preValues 中
    values.forEach((it) => {
      preValues[it.varId] = it.varValue
    })
  }

  gridData.value = list.filter(item => item.varDirection === 0).map(item => ({
    ...item,
    form: {
      types: 'Any',
      name: item.id,
      key: item.id,
      title: item.varName,
      value: preValues[item.id]?.value ?? [],
      formType: {
        type: 'INPUT_VARIABLE_PYTHON',
      },
    },
  }))
}, { immediate: true })

watch(() => gridData.value, (newGridData) => {
  const values: ParamValues = toRaw(newGridData).map(item => ({
    varId: item.id,
    varName: item.varName,
    varValue: {
      rpa: 'special',
      value: toRaw(item.form.value) as Array<any>,
    },
  }))

  if (isEqual(values, props.renderData.value)) {
    return
  }

  emits('refresh', values)
}, { deep: true })
</script>

<!-- 输入参数可支持普通文本模式、python模式和变量选择填入 -->
<template>
  <VxeGrid v-bind="gridOptions" class="params-table" :data="gridData">
    <template #value_default="{ row }">
      <AtomConfig :key="row.id" :form-item="row.form" size="small" />
    </template>
  </VxeGrid>
</template>

<style lang="scss" scoped>
.params-table {
  --vxe-ui-table-row-height-mini: 32px;
  --vxe-ui-table-column-padding-mini: 5px 0;

  overflow: hidden;
  width: 100%;
}
</style>
