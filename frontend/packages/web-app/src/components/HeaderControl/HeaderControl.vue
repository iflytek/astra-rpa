<script setup lang="ts">
import { NiceModal } from '@rpa/components'
import { Tooltip } from 'ant-design-vue'

import { SettingCenterModal } from '@/components/SettingCenterModal'
import { VUE_APP_COMMANDER, VUE_APP_HELP } from '@/constants'
import { utilsManager } from '@/platform'
import useUserSettingStore from '@/stores/useUserSetting.ts'

import MessageTip from '../MesssageTip/Index.vue'

import UserInfo from './UserInfo.vue'

// 控制按钮显示
defineProps({
  help: {
    type: Boolean,
    default: false,
  },
  setting: {
    type: Boolean,
    default: true,
  },
  control: {
    type: Boolean,
    default: false,
  },
  message: {
    type: Boolean,
    default: false,
  },
  userInfo: {
    type: Boolean,
    default: true,
  },
})

useUserSettingStore()

function handleOpenSetting() {
  NiceModal.show(SettingCenterModal)
}

function handleToControl() {
  const url = location.hostname.includes('iflyrpa') ? `${location.origin}/admin/` : VUE_APP_COMMANDER
  utilsManager.openInBrowser(url)
}

function handleHelpInfo() {
  utilsManager.openInBrowser(VUE_APP_HELP)
}
</script>

<template>
  <Tooltip v-if="help" :title="$t('helperCenter')">
    <span class="app_control__item" @click="handleHelpInfo">
      <rpa-icon name="help-circle" />
    </span>
  </Tooltip>
  <Tooltip v-if="setting" :title="$t('setting')">
    <span class="app_control__item" @click="handleOpenSetting">
      <rpa-icon name="setting" />
    </span>
  </Tooltip>

  <Tooltip v-if="control" :title="$t('excellenceCenter')">
    <span class="app_control__item" @click="handleToControl">
      <rpa-icon name="desktop" />
    </span>
  </Tooltip>
  <span v-if="message" class="app_control__item">
    <MessageTip />
  </span>
  <span v-if="userInfo" class="app_control__item">
    <UserInfo />
  </span>
</template>

<style lang="scss" scoped>
.app_control__item {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 28px;
  width: 28px;
  margin-left: 12px;
  &:hover {
    background-color: $color-fill-secondary;
    border-radius: 8px;
  }
}
</style>
