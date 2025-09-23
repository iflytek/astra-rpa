import Sdk from 'casdoor-js-sdk'

import { getBaseURL } from '@/api/http/env'
import { casdoorLogout, casdoorSignin, casdoorUserinfo, setRpaLocalAuth } from '@/api/login/casdoor'
import { DESIGNER } from '@/constants/menu'
import { useRoutePush } from '@/hooks/useCommonRoute'

import type { IAuthService } from '../types'

import { redirectToLogin } from './unauthorize'

export class CasdoorAuthService implements IAuthService {
  private readonly serverUrl = getBaseURL()
  private readonly casdoorSDK: InstanceType<typeof Sdk>

  constructor() {
    const config = {
      serverUrl: this.serverUrl,
      clientId: 'e3ba6fec42cfe996121f',
      appName: 'example-app',
      organizationName: 'example-org',
      redirectPath: '/',
    }
    this.casdoorSDK = new Sdk(config)
  }

  private isLoggedIn(): boolean {
    const token = this.getToken()
    return token !== null && token.length > 0
  }

  private getToken(): string | null {
    return localStorage.getItem('accessToken')
  }

  private setToken(token: string): void {
    localStorage.setItem('accessToken', `Bearer ${token}`)
  }

  private async setLocalAuth(): Promise<void> {
    try {
      await setRpaLocalAuth({ authorization: `${this.getToken()}` })
    }
    catch { }
  }

  private async handleCallback(code: string, state: string): Promise<void> {
    try {
      const response = await casdoorSignin({ code, state })
      const accessToken = response.data
      this.setToken(accessToken)
      this.setLocalAuth()
      useRoutePush({ name: DESIGNER })
    }
    catch (error) {
      console.error('Casdoor登录失败:', error)
    }
  }

  async checkLogin(callback: () => void): Promise<void> {
    if (this.isLoggedIn()) {
      this.setLocalAuth()
      callback && callback()
      return
    }
    this.login()
  }

  async login(): Promise<void> {
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const state = urlParams.get('state')

    if (code && state) {
      await this.handleCallback(code, state)
    }
    else {
      await redirectToLogin()
    }
  }

  async logout(): Promise<void> {
    try {
      await casdoorLogout()
      localStorage.removeItem('accessToken')
      window.location.href = '/'
    }
    catch (error) {
      console.error('Casdoor登出失败:', error)
    }
  }

  async getUserName(): Promise<string> {
    try {
      const res = await casdoorUserinfo() as any
      return res?.data.displayName || '--'
    }
    catch (error) {
      console.error('获取用户信息失败:', error)
      return null
    }
  }
}
