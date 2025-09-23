<script setup lang="ts">
import { ref, watch } from 'vue'

import useUserSettingStore from '@/stores/useUserSetting'

import LanguageCheck from './languageCheck.vue'
import PanelCard from './panelCard.vue'
import ThemeCheck from './themeCheck.vue'

const panelOption = ref([
  {
    key: 'startupSettings',
    title: 'startupSettings',
    description: 'automaticStartup',
    value: false,
  },
  {
    key: 'closeMainPage',
    title: 'closeMainPage',
    description: 'minimizeToTray',
    value: false,
  },
  {
    key: 'hideLogWindow',
    title: 'logWindow',
    description: 'hideLogWindow',
    value: false,
  },
  {
    key: 'hideDetailLogWindow',
    title: 'detailLogWindow',
    description: 'hideDetailLogWindow',
    value: false,
  },
  {
    key: 'autoSave',
    title: 'autosave',
    description: 'enableAutosave',
    value: true,
  },
])

watch(
  () => useUserSettingStore().userSetting.commonSetting,
  (newVal) => {
    panelOption.value = panelOption.value.map((panel) => {
      return {
        ...panel,
        value: newVal[panel.key],
      }
    })
  },
  { immediate: true },
)
</script>

<template>
  <div class="space-y-3">
    <ThemeCheck />
    <LanguageCheck />
    <PanelCard
      v-for="(panel, index) in panelOption"
      :key="index"
      v-model:value="panel.value"
      :title="$t(panel.title)"
      :description="$t(panel.description)"
      @input="
        (value) => useUserSettingStore().changeCommonConfig(panel.key, value)
      "
    />
  </div>
</template>
