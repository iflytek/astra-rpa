import { onBeforeUnmount, ref } from 'vue'

import { updateHotkeysSetting } from '@/utils/registerHotkeys'

import type { ShortcutItemMap } from '@/components/ShortcutInput/types.ts'
import { commonKeys, shortcuts } from '@/constants/shortcuts'
import useUserSettingStore from '@/stores/useUserSetting.ts'

export function useShortcutData() {
  const shortcutForm = ref()
  const formData = ref(shortcuts)

  // 读取本地快捷键设置，并更新当前修改的快捷键
  const saveShortCutData = () => {
    const shortcutFormData = {}
    Object.keys(formData.value).forEach((shortKey) => {
      shortcutFormData[shortKey] = {
        value: formData.value[shortKey].value,
        text: formData.value[shortKey].text,
      }
    })
    const newSetting = { shortcutConfig: shortcutFormData }
    useUserSettingStore().saveUserSetting(newSetting)
    updateHotkeysSetting()
  }

  // 同步本地与当前表单的快捷键数据，避免使用直接赋值造成数据无法更新属性key
  const getShortCutData = () => {
    const localShortcuts = useUserSettingStore().userSetting.shortcutConfig || {}
    Object.keys(formData.value).forEach((shortKey) => {
      if (localShortcuts[shortKey]) {
        // 存在本地数据即可覆盖数据
        formData.value[shortKey].value = localShortcuts[shortKey].value
        formData.value[shortKey].text = localShortcuts[shortKey].text
      }
    })
    validateAll()
  }

  const validate = (itemData: ShortcutItemMap) => {
    // validateText存储验证结果
    let validateText = ''
    // 进行验证
    const value = itemData.text.replace(/\s/g, '').toLowerCase()
    if (!['点击设置按键', '输入按键', '输入新的按键'].includes(value)) {
      const inx = commonKeys.indexOf(value)
      if (inx > -1) {
        validateText += `快捷键与常见快捷键或软件内置快捷键${commonKeys[inx]}冲突!`
      }
      Object.keys(formData.value).forEach((key) => {
        const item = formData.value[key]
        if (item.id !== itemData.id) {
          const { text, name } = item
          if (value === text.replace(/\s/g, '').toLowerCase()) {
            validateText += `快捷键与${name}冲突!`
          }
        }
      })
    }

    formData.value[itemData.id].validate = validateText
  }

  const validateAll = () => {
    Object.keys(formData.value).forEach((key) => {
      validate(formData.value[key])
    })
  }

  const setActive = (itemData: ShortcutItemMap, status = true) => {
    Object.keys(formData.value).forEach((key) => {
      formData.value[key].active = itemData.id === formData.value[key].id ? status : false
    })
  }

  getShortCutData()

  onBeforeUnmount(() => {
    saveShortCutData()
  })

  return {
    shortcutForm,
    formData,
    validate,
    setActive,
    validateAll,
  }
}
