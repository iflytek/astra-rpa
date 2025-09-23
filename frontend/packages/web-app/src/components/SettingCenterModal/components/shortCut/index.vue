<script setup lang="ts">
import ShortCutInput from '@/components/ShortcutInput/Index.vue'
import type { ShortcutItemMap } from '@/components/ShortcutInput/types.ts'

import { useShortcutData } from './hooks/useShortcutData'

const {
  shortcutForm,
  formData,
  validateAll,
  setActive,
} = useShortcutData()

function handleChange() {
  validateAll()
}

function handleBlur(itemData: ShortcutItemMap) {
  setActive(itemData, false)
}

function handleFocus(itemData: ShortcutItemMap) {
  setActive(itemData)
}
</script>

<template>
  <a-form
    ref="shortcutForm"
    :label-col="{ span: 5 }"
    :wrapper-col="{ span: 19 }"
    :colon="false"
  >
    <template v-for="key in Object.keys(formData)">
      <a-form-item
        v-if="formData[key].showSettingCenter"
        :key="key"
        :label="$t(formData[key].name)"
      >
        <ShortCutInput v-model="formData[key]" :form-data="formData" @change="handleChange" @focus="handleFocus" @blur="handleBlur" />
      </a-form-item>
    </template>
  </a-form>
</template>

<style lang="scss">
.Shortcut {
  &-title {
    font-weight: bold;
    margin-bottom: 20px;
    color: #000;
  }
}
</style>
