import { blob2Text } from '@/utils/common'

import { fileRead, fileWrite } from '@/api/resource'

import http from './http'
import { getRootBaseURL } from './http/env'

const useSettingPath = './.setting.json'

export async function getUserSetting() {
  try {
    const { data } = await fileRead({ path: useSettingPath })
    const result = await blob2Text<string>(data)
    return JSON.parse(result || '{}')
  }
  catch {
    return {}
  }
}

export async function setUserSetting(params: RPA.UserSetting) {
  return fileWrite({ path: useSettingPath, mode: 'w', content: JSON.stringify(params) })
}

/**
 * @returns 获取自动启动状态
 */
export async function autoStartStatus() {
  const res = await http.post<{ autostart: boolean }>('/scheduler/window/auto_start/check', null, { baseURL: getRootBaseURL() })

  return res.data.autostart
}
/**
 * @returns 设置自动启动
 */
export function autoStartEnable() {
  return http.post('/scheduler/window/auto_start/enable', null, { baseURL: getRootBaseURL() })
}
/**
 * @returns 关闭自动启动
 */
export function autoStartDisable() {
  return http.post('/scheduler/window/auto_start/disable', null, { baseURL: getRootBaseURL() })
}
/**
 * @returns 检查视频文件是否存在
 */
export function checkVideoPaths(data) {
  return http.post('/scheduler/video/play', data, { baseURL: getRootBaseURL(), toast: false })
}

/**
 * @description: 邮箱短信设置
 */
export function toolsInterfacePost(data) {
  return http.post('/scheduler/alert/test', data, { baseURL: getRootBaseURL() })
}

/**
 * @description: 获取Api Key列表数据
 */
export function getApis(params) {
  // return http.get('/rpaai/get-key', params)
  return http.get('/rpa-openapi/api-keys/get', params)
}

/**
 * @description: 删除API Key
 */
export function deleteAPI(params) {
  // return http.post('/rpaai/remove-key', params)
  return http.post('/rpa-openapi/api-keys/remove', params)
}

/**
 * @description: 新增API Key
 */
export function createAPI(params) {
  // return http.post('/rpaai/add-key', params)
  return http.post('/rpa-openapi/api-keys/create', params)
}
