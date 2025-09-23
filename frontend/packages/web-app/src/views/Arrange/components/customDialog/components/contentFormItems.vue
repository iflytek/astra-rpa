<script lang="ts" setup>
import { message } from 'ant-design-vue'
import { cloneDeep } from 'lodash-es'
import { inject, nextTick, ref } from 'vue'
import draggable from 'vuedraggable'

import type { Fun } from '@/types/common.js'
import { genNonDuplicateID } from '@/views/Arrange/utils/index'

import { limitFormsNum } from '../config/index.ts'
import type { FormItemConfig } from '../types/index.ts'
import { dialogFormConfig, getRightIndex } from '../utils/index.ts'

import FormItem from './formItem.vue'

const { dialogData, updateDialogDataFormList } = inject('dialogData') as { dialogData: any, updateDialogDataFormList: any }
const { selectedFormItem, updateSelectedFormItem } = inject('selectedFormItem') as { selectedFormItem: FormItemConfig, updateSelectedFormItem: Fun }
const hoveredPreviewItem = ref(null as FormItemConfig | null) // 当前悬浮的预览项

function setPreViewItem(item?: FormItemConfig) {
  hoveredPreviewItem.value = item
}

function dbClick(item: FormItemConfig) {
  if (dialogData.value?.formList.length >= limitFormsNum) {
    message.warning('最多只能添加50个表单控件')
    return
  }
  const dialogItem = cloneDeep(item)
  dialogItem.id = genNonDuplicateID()
  const bindKey = dialogItem?.bind?.key
  bindKey && (dialogItem.bind.value[0].value = `${bindKey}_${getRightIndex(dialogData.value?.formList, bindKey)}`)
  let addIdx = dialogData.value?.formList.length - 1
  if (selectedFormItem.value) {
    addIdx = dialogData.value?.formList.findIndex(i => i.id === selectedFormItem.value.id)
  }
  if (addIdx > -1) {
    updateDialogDataFormList('splice', addIdx + 1, 0, dialogItem)
  }
  else {
    updateDialogDataFormList('push', dialogItem)
  }
  updateSelectedFormItem(null)
  nextTick(() => {
    updateSelectedFormItem(dialogItem)
  })
}
function handleStart() {
  if (dialogData.value?.formList.length >= limitFormsNum) {
    message.warning('最多只能添加50个表单控件')
  }
}
</script>

<template>
  <div class="dialog-modal_formItems">
    <div class="formItems">
      <div class="header">
        表单控件
      </div>
      <draggable
        item-key="id"
        :list="dialogFormConfig"
        filter=".forbid"
        :group="{ name: 'dialog', pull: 'clone', put: false }"
        class="formItemList"
        :touch-start-threshold="3"
        :sort="false"
        @start="handleStart"
      >
        <template #item="{ element: item }">
          <div
            class="form-item bg-[#F3F3F7] dark:bg-[#FFFFFF]/[.08] hover:bg-[#5D59FF]/[.35] rounded-md"
            @dblclick="() => dbClick(item)"
            @mouseenter="() => setPreViewItem(item)"
            @mouseleave="() => setPreViewItem()"
          >
            <span>{{ item.dialogFormName }}</span>
          </div>
        </template>
      </draggable>
    </div>
    <div class="form-item-preview">
      <div class="header">
        预览
      </div>
      <div v-if="hoveredPreviewItem" class="preview-item">
        <div v-if="hoveredPreviewItem.dialogFormType !== 'TEXT_DESC'" class="mb-1" :style="`${!hoveredPreviewItem?.label.value[0].value ? 'color:#f00;' : ''}`">
          <span v-if="hoveredPreviewItem?.required?.value" class="starRequired">*</span>
          {{ !hoveredPreviewItem?.label.value[0].value ? '请配置标题' : hoveredPreviewItem.label.value[0].value }}
        </div>
        <FormItem :option="hoveredPreviewItem" />
      </div>
      <div v-else class="preview-empty text-[#000000]/[.65] dark:text-[#FFFFFF]/[.65]">
        悬停控件展示预览信息
      </div>
    </div>
  </div>
</template>

<style lang="scss">
</style>
