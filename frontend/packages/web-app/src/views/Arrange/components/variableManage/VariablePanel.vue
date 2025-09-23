<script setup lang="ts">
import { message } from 'ant-design-vue'
import type { ColumnType } from 'ant-design-vue/es/table'
import { useTranslation } from 'i18next-vue'
import { cloneDeep } from 'lodash-es'
import { computed, ref, toRaw } from 'vue'

import { GLOBAL_VAR_IN_TYPE } from '@/constants/atom'
import { useFlowStore } from '@/stores/useFlowStore'
import { useProcessStore } from '@/stores/useProcessStore'
import { useVariableStore } from '@/stores/useVariableStore'
import { getFlowVariable } from '@/views/Arrange/utils/generateData'

import { paginationConfig } from '../tools/components/constant'

const { t } = useTranslation()
const flowStore = useFlowStore()
const processStore = useProcessStore()
const variableStore = useVariableStore()

const keyword = ref('')

const columns: ColumnType<RPA.GlobalVariable>[] = [
  {
    title: t('varName'),
    dataIndex: 'varName',
    ellipsis: true,
    key: 'varName',
  },
  {
    title: t('varType'),
    dataIndex: 'varType',
    key: 'varType',
  },
  {
    title: t('varValue'),
    dataIndex: 'varValue',
    key: 'varValue',
    ellipsis: true,
  },
  {
    title: t('varDescribe'),
    dataIndex: 'varDescribe',
    key: 'varDescribe',
    ellipsis: true,
  },
  {
    title: t('operate'),
    dataIndex: 'operate',
    key: 'operate',
    width: '100px',
  },
]

const dataSource = computed(() => {
  const variableList = toRaw(variableStore.globalVariableList)

  if (keyword.value.trim()) {
    return variableList.filter(item =>
      item.varName
        .toLocaleLowerCase()
        .includes(keyword.value.toLocaleLowerCase()),
    )
  }

  return variableList
})

const editableData = ref<RPA.GlobalVariable | null>(null)

function judgeVarName({ varName, globalId }: RPA.GlobalVariable) {
  const flowVar = getFlowVariable()

  // 判断是否存在同名的流程变量
  const isFlowNameEqual = flowVar.some(item => item.name === varName)

  if (isFlowNameEqual)
    return true

  // 判断是否存在同名的全局变量
  return dataSource.value.some(item => item.varName === varName && item.globalId !== globalId)
}

async function handleSave(record: RPA.GlobalVariable) {
  if (!editableData.value.varName.trim())
    return message.error('变量名不能为空')
  if (judgeVarName(editableData.value))
    return message.error('变量名已存在')

  await variableStore.saveGlobalVariableList(editableData.value)

  flowStore.flowVariableUpdate({
    varName: record.varName,
    newVarName: editableData.value.varName,
    varType: GLOBAL_VAR_IN_TYPE,
    type: 'rename',
  })

  editableData.value = null
}

function generateTableCellText(column: ColumnType<RPA.GlobalVariable>, text: string, record: RPA.GlobalVariable) {
  if (column.dataIndex === 'varType') {
    return processStore.globalVarTypeList[record.varType]?.desc
  }

  return text
}

async function addGloablVar() {
  editableData.value = cloneDeep(await variableStore.addGlobalVariableList())
}

function handleEdit(record: RPA.GlobalVariable) {
  editableData.value = cloneDeep(record)
}

async function handleReduceRecord(item: RPA.GlobalVariable) {
  await variableStore.deleteGlobalVariableList(item.globalId)

  flowStore.flowVariableUpdate({
    varName: item.varName,
    varType: GLOBAL_VAR_IN_TYPE,
    type: 'delete',
  })
}

const editableColumn: Array<keyof RPA.GlobalVariable> = ['varName', 'varType', 'varValue', 'varDescribe']
</script>

<template>
  <div class="variable-panel">
    <nav class="variable-management-header mb-3 flex justify-between items-center">
      <a-input
        v-model:value="keyword"
        allow-clear
        class="flex-1 leading-6"
        :placeholder="t('enterVaruableName')"
      >
        <template #prefix>
          <rpa-icon name="search" class="dark:text-[rgba(255,255,255,0.25)]" />
        </template>
      </a-input>
      <rpa-hint-icon name="python-package-plus" class="global-variable-plus text-[12px]" enable-hover-bg @click="addGloablVar">
        <template #suffix>
          {{ t("addVariable") }}
        </template>
      </rpa-hint-icon>
    </nav>
    <a-table size="small" :data-source="dataSource" :columns="columns" :pagination="paginationConfig">
      <template #bodyCell="{ column, text, record }">
        <template v-if="editableColumn.includes(column.dataIndex as keyof RPA.GlobalVariable)">
          <template v-if="editableData?.globalId === record.globalId">
            <a-select
              v-if="column.dataIndex === 'varType'" v-model:value="editableData.varType" class="w-full"
              :field-names="{ label: 'desc', value: 'key' }" :options="processStore.globalVarTypeOption"
            />
            <a-input v-else v-model:value="editableData[column.dataIndex as string]" />
          </template>
          <template v-else>
            {{ generateTableCellText(column, text, record as RPA.GlobalVariable) || "--" }}
          </template>
        </template>
        <template v-else>
          <div class="space-x-2">
            <a
              v-if="editableData?.globalId === record.globalId" class="!text-primary hover:opacity-80"
              @click="handleSave(record as RPA.GlobalVariable)"
            >
              {{ t("save") }}
            </a>
            <a v-else class="!text-primary hover:opacity-80" @click="() => handleEdit(record as RPA.GlobalVariable)">
              {{ t("edit") }}
            </a>
            <a-popconfirm
              :overlay-style="{ width: '260px' }" :title="t('confirmDeleteVariables')"
              :description="t('confirmDeleteVariablesInfo')"
              :on-confirm="() => handleReduceRecord(record as RPA.GlobalVariable)"
            >
              <a class="!text-primary hover:opacity-80">{{ t("delete") }}</a>
            </a-popconfirm>
          </div>
        </template>
      </template>
    </a-table>
  </div>
</template>

<style lang="scss" scoped>
.variable-panel {
  --table-head-default: rgba(0, 0, 0, 0.45);
  --table-body-default: rgba(0, 0, 0, 0.85);

  .dark & {
    --table-head-default: rgba(255, 255, 255, 0.45);
    --table-body-default: rgba(255, 255, 255, 0.85);
  }
}

.global-variable-plus {
  height: 24px;
  font-weight: 400;
  line-height: 24px;
  margin-left: 10px;
}

:deep(.ant-table-thead > tr > th) {
  font-size: 12px;
  color: var(--table-head-default);
  background: transparent;
}

:deep(.ant-table-tbody > tr > td) {
  font-size: 14px;
  color: var(--table-body-default);
}

.ant-table-thead > tr > th,
.ant-table-tbody > tr > td {
  padding: 14px 16px;
  font-weight: 400;
}
</style>
