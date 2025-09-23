<script setup lang="ts">
import type { RadioChangeEvent } from 'ant-design-vue'
import { RadioGroup } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

import useUserSettingStore from '@/stores/useUserSetting'

const { t } = useTranslation()
const userSettingStore = useUserSettingStore()
const { userSetting } = storeToRefs(userSettingStore)

const options = computed(() => ([
  {
    label: t('settingCenter.minimizeToTray'),
    value: true,
  },
  {
    label: t('settingCenter.exitProgram'),
    value: false,
  },
]))

function change(e: RadioChangeEvent) {
  userSettingStore.changeCommonConfig('closeMainPage', e.target.value as boolean)
}
</script>

<template>
  <div class="mt-[10px]">
    {{ $t('settingCenter.closeWindowTips') }}
    <RadioGroup
      v-model:value="userSetting.commonSetting.closeMainPage"
      class="mt-[10px]"
      :options="options"
      @change="change"
    />
  </div>
</template>
