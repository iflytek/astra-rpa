import axios from 'axios'

import { getBaseURL, getRootBaseURL } from '@/api/http/env'
import { utilsManager, windowManager } from '@/platform'

let casdoorUrl = ''

export function fileRead(data: { path: string }) {
  return axios.post(
    `${getRootBaseURL()}/scheduler/file/read`,
    data,
    {
      responseType: 'blob',
      timeout: 5000000,
    },
  )
}
async function getCasdoorServerUrl() {
  const res = await utilsManager.getAppPath()
  const confPath = `${res}resources\\conf.json`
  casdoorUrl = 'http://localhost:8000'
  try {
    const res = await utilsManager.readFile(confPath)
    const conf = JSON.parse(new TextDecoder().decode(res as Uint8Array) || '{}')
    casdoorUrl = conf.casdoor
  }
  catch (error) {
    console.log('error', error)
  }
  console.log('casdoorUrl', casdoorUrl)
}

getCasdoorServerUrl()

async function casdoorRedirectUrl() {
  const res = await axios.get(`${getBaseURL()}/robot/user/api/redirect-url`)
  return res.data
}

async function redirectToLogin(): Promise<void> {
  try {
    const res = await casdoorRedirectUrl() as any
    const signinUrl = `${casdoorUrl}${res.data}`
    if (signinUrl) {
      if (windowManager) {
        await windowManager.restoreLoginWindow()
        await windowManager.showDecorations()
      }
      window.location.href = signinUrl
    }
  }
  catch {
    // console.error('casdoorRedirectUrl:', error)
  }
}

function getHttpAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('accessToken')
  return token
    ? {
        Authorization: token,
      }
    : null
}

function checkHttpResponse(response: any): boolean {
  // 服务接口返回500时，重定向到登录页面
  const isExpired = response?.data.code === '800000'
  if (isExpired) {
    redirectToLogin()
  }
  return isExpired
}

export { checkHttpResponse, getHttpAuthHeader, redirectToLogin }
