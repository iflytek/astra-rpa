import type { BasicColorSchema } from '@vueuse/core'
import { message } from 'ant-design-vue'
import deepmerge from 'deepmerge'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { autoStartDisable, autoStartEnable, autoStartStatus, getUserSetting, setUserSetting } from '@/api/setting'

export type Theme = BasicColorSchema

export const DEFAULT_FORM: RPA.VideoFormMap = {
  saveType: true,
  enable: false,
  scene: 'fail',
  cutTime: 30,
  fileClearTime: 7,
  // maxRecordingTime: 10,
  filePath: '',
}

const useUserSettingStore = defineStore('useUserSetting', () => {
  const userSetting = ref<RPA.UserSetting>({
    commonSetting: { // 常规设置
      startupSettings: false, // 启动项设置 - 引擎接口获取存储，true 开启自启动，false-关闭开机自启动
      closeMainPage: false, // true-最小化托盘  false-退出应用
      hideLogWindow: false, // 运行时的右下角日志窗口 true-开启隐藏  false-关闭隐藏
      hideDetailLogWindow: false, // 运行完的详细日志窗口 true-开启隐藏  false-关闭隐藏
      autoSave: true, // 自动保存 true-开启  false-关闭
      theme: 'auto',
    },
    shortcutConfig: {}, // 快捷键设置
    videoForm: DEFAULT_FORM, // 录屏设置
    msgNotifyForm: {}, // 消息通知设置
  })

  // 获取常规设置
  const getSetting = async () => {
    const [autostart, setting] = await Promise.all([
      autoStartStatus(),
      getUserSetting(),
    ])

    userSetting.value = deepmerge.all<RPA.UserSetting>([
      userSetting.value,
      setting,
      { commonSetting: { startupSettings: autostart } },
    ],
    )
  }

  const saveUserSetting = (params: object) => {
    userSetting.value = {
      ...userSetting.value,
      ...params,
    }
    setUserSetting(userSetting.value)
  }

  // 修改常规设置
  const changeCommonConfig = async (key: string, value: boolean) => {
    if (key === 'startupSettings') {
      const func = value ? autoStartEnable : autoStartDisable
      const res = await func()
      message.success(res.data.tips)
      getSetting()

      return
    }

    saveUserSetting({
      commonSetting: {
        ...userSetting.value.commonSetting,
        [key]: value,
      },
    })
  }

  getSetting()

  return {
    userSetting,
    saveUserSetting,
    changeCommonConfig,
  }
})

export default useUserSettingStore
