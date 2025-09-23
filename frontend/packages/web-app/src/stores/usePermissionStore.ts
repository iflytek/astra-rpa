import { defineStore } from 'pinia'
/**
 * 全局权益信息的维护
 */
import { ref } from 'vue'

import type { AnyObj } from '@/types/common'

export const usePermissionStore = defineStore('running', () => {
  const permissionAction = ref({}) // 权益信息
  const setPermission = (value: AnyObj) => {
    permissionAction.value = value
  }

  return {
    permissionAction,
    setPermission,
  }
})
