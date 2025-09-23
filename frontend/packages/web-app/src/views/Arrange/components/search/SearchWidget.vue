<!-- @format -->
<script setup lang="ts">
import { ArrowDownOutlined, ArrowUpOutlined, CloseOutlined } from '@ant-design/icons-vue'
import { Divider } from 'ant-design-vue'
import { isNil } from 'lodash-es'
import { computed, ref } from 'vue'

const { total, active, value } = defineProps({
  value: {
    type: String,
    default: '',
  },
  total: {
    type: Number,
    default: 0,
  },
  active: {
    type: Number,
    default: 0,
  },
})

const emits = defineEmits(['close', 'input', 'previous', 'next'])

const inputText = ref(value)
const inputRef = ref(null)

const calculateCount = computed(() => {
  if (!inputText.value)
    return undefined
  return total === 0 ? '0/0' : `${active}/${total}`
})

function close() {
  emits('close')
}

function up() {
  emits('previous')
}

function down() {
  emits('next')
}

function updateValue() {
  emits('input', inputText.value)
}

function focus() {
  inputRef.value.focus()
}

defineExpose({
  focus,
})
</script>

<template>
  <a-card class="search-widget">
    <div class="search-widget-container">
      <a-input
        ref="inputRef"
        v-model:value="inputText"
        auto-focus
        :placeholder="$t('search')"
        @input="updateValue"
        @press-enter="down"
      />
      <span v-if="!isNil(calculateCount)" class="search-widget-total">{{ calculateCount }}</span>
      <Divider type="vertical" class="search-widget-divider" />
      <div class="search-widget-icon" @click="up">
        <ArrowUpOutlined />
      </div>
      <div class="search-widget-icon" @click="down">
        <ArrowDownOutlined />
      </div>
      <div class="search-widget-icon" @click="close">
        <CloseOutlined />
      </div>
    </div>
  </a-card>
</template>

<style scoped lang="scss">
.search-widget {
  :deep(.ant-card-body) {
    padding: 3px 10px 3px 0;
    width: 310px;
    border-radius: 8px !important;
    position: absolute;
    right: 0;
    top: 20px;
    background-color: #fff;
    box-shadow: 0px 0px 10px 0px #e7e8ec;
  }

  :deep(.ant-input) {
    border: none;
    box-shadow: none;
    flex: 1;
    font-size: 12px;
  }

  &-container {
    display: flex;
    align-items: center;
  }

  &-total {
    margin-right: 15px;
  }

  &-divider {
    margin: 0 5px 0 0;
    height: 20px;
  }

  &-icon {
    font-size: 12px;
    display: inline-flex;
    cursor: pointer;
    padding: 5px;
    margin-left: 5px;

    &:hover {
      color: $color-primary;
    }
  }
}
</style>
