<script setup lang="ts">
import { CaretDownOutlined, CaretUpOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { ref, watch } from 'vue'

const { title } = defineProps({
  title: {
    type: String,
    default: '',
  },
  leafKey: {
    type: String,
    default: '',
  },
})
const emits = defineEmits(['getInputVal'])

watch(
  () => title,
  (newVal) => {
    titleVal.value = {}
    leaf.value = []
    generateTreeInput(newVal)
  },
  { deep: true },
)

const leaf = ref([])
const titleVal = ref({})

function inputChange() {
  const intArr = []
  Object.keys(titleVal.value).filter((item) => {
    if (item.includes('int')) {
      intArr.push(titleVal.value[item])
      return true
    }
    return false
  })
  const flag = intArr.every(val => Number.isInteger(val) && Number(val) > 0)
  if (!flag)
    return message.error('请输入正整数')
  emits('getInputVal', titleVal.value)
}

function generateTreeInput(title = '') {
  const reg = /@\{[^:]+:[^}]+\}/g
  const matchArr = title.match(reg)
  if (!matchArr)
    return leaf.value.push(title)
  const strArr = title.split(reg)
  for (let i = 0; i < strArr.length; i++) {
    leaf.value.push(strArr[i])
    if (i < matchArr.length) {
      leaf.value.push(`@(${matchArr[i]})`)
      titleVal.value[`@(${matchArr[i]})`] = matchArr[i].includes('int') ? 1 : ''
    }
  }
}
generateTreeInput(title)
</script>

<template>
  <template v-for="item in leaf" :key="item">
    <template v-if="item.includes('@')">
      <a-input-number
        v-if="item.includes('int')" v-model:value="titleVal[item]" class="h-4 w-10 input-number"
        :bordered="false" size="small" :min="1" :max="999" @click.stop @change="inputChange"
      >
        <template #upIcon>
          <CaretUpOutlined :style="{ fontSize: '8px' }" @click.stop />
        </template>
        <template #downIcon>
          <CaretDownOutlined :style="{ fontSize: '8px' }" @click.stop />
        </template>
      </a-input-number>
      <a-input
        v-if="item.includes('str')" v-model:value="titleVal[item]" class="h-4 w-12 input-number"
        :bordered="false" size="small" @click.stop @change="inputChange"
      />
    </template>
    <template v-else>
      {{ item }}
    </template>
  </template>
</template>

<style lang="scss" scoped>
.input-number {
  :deep(.ant-input-number-input-wrap) {
    height: 100%;
  }

  :deep(.ant-input-number-input) {
    height: 100%;
  }

  :deep(.ant-input-number-handler-wrap) {
    width: 16px;
  }

  :deep(.ant-input-number-handler) {
    border: 0;
  }
}
</style>
