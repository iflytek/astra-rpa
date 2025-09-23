<script lang="ts" setup>
import { QuestionCircleOutlined } from '@ant-design/icons-vue'
import type { Rule } from 'ant-design-vue/es/form'
import { ref } from 'vue'

import { getWeightedLength, getWeightText } from '@/utils/common'

const props = defineProps({
  formOption: {
    type: Object,
  },
})

const formRef = ref()
const rules: Record<string, Rule[]> = {
  pickName: [
    {
      message: '请输入元素名称',
      trigger: 'blur',
      validator: async (_rule, value) => {
        if (!value.replace(/\s+/g, '')) {
          return Promise.reject(new Error('请输入元素名称'))
        }
        else {
          return Promise.resolve()
        }
      },
    },
  ],
}

function validateName() {
  return new Promise((resolve) => {
    formRef.value.validateFields(['pickName']).then((valid) => {
      if (valid) {
        resolve(true)
      }
    })
  })
}

function inputChange(e) {
  const originLength = getWeightedLength(e.target.value)
  if (originLength >= 32) {
    e.target.value = getWeightText(32, e.target.value)
    props.formOption.pickName = e.target.value
    return false
  }
}

defineExpose({
  validateName,
})
</script>

<template>
  <a-form ref="formRef" :key="formOption.pikName" class="form-wrapper font-size-12" :rules="rules" :model="formOption" :label-col="{ span: 5 }" :wrapper-col="{ span: 14 }" label-align="left">
    <a-form-item :label="$t('elementName')" name="pickName">
      <a-input v-model:value="formOption.pickName" autocomplete="off" class="font-size-12" :maxlength="32" :placeholder="$t('enterElementName')" @change="inputChange" />
    </a-form-item>
    <a-form-item :label="$t('customization')">
      <a-radio-group v-model:value="formOption.editXPathType" size="small">
        <a-radio-button v-for="item in formOption.customOptions" :key="item.lable" :value="item.value" class="font-size-12">
          {{ $t(item.label) }}
        </a-radio-button>
      </a-radio-group>
    </a-form-item>
    <a-form-item v-if="formOption.pickType === 'web'" :label="$t('matchingMethod')">
      <a-checkbox-group v-model:value="formOption.matchTypes" size="small" class="flex flex-nowrap" :options="formOption.matchOptions">
        <template #label="{ label, tip }">
          <span class="font-size-12">{{ $t(label) }}</span>
          <a-tooltip placement="top" :title="$t(tip)">
            <QuestionCircleOutlined class="ml-1" />
          </a-tooltip>
        </template>
      </a-checkbox-group>
    </a-form-item>
  </a-form>
</template>

<style scoped>
.font-size-12 {
  font-size: 12px;
}

.ant-form-item {
  margin-bottom: 10px;
}
.ant-form-item:last-child {
  margin-bottom: 0;
}

.ant-btn-sm {
  font-size: 12px;
}

.form-wrapper {
  height: auto;
  font-size: 12px;
}

.font-small {
  font-size: 12px;
}

.check-select {
  height: 28px;
}

:deep(.ant-select-single .ant-select-selector) {
  height: 28px;
  font-size: 12px;
}

:deep(.ant-select-single.ant-select-sm.ant-select-show-arrow .ant-select-selection-item) {
  font-size: 12px;
}
</style>
