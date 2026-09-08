/**
 * 用户状态管理（Pinia）
 *
 * 存储登录态：Token、用户信息、菜单树。
 * Token 同时持久化到 localStorage，页面刷新后从 localStorage 恢复，
 * 再通过 fetchUserInfo 拉取最新用户信息（避免 Token 被篡改后的权限残留）。
 */
import { defineStore } from 'pinia'
import { login as apiLogin, getUserInfo, getMenuTree, type MenuItem, type LoginResult } from '@/api/auth'

type UserInfo = LoginResult['user']

interface UserState {
  token: string
  userInfo: UserInfo | null
  menus: MenuItem[]
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('access_token') || '',
    userInfo: null,
    menus: []
  }),
  actions: {
    async login(username: string, password: string) {
      const res = await apiLogin({ username, password })
      this.token = res.access_token
      localStorage.setItem('access_token', res.access_token)
      localStorage.setItem('refresh_token', res.refresh_token)
      this.userInfo = res.user
      return res
    },
    async fetchUserInfo() {
      this.userInfo = await getUserInfo()
      return this.userInfo
    },
    async fetchMenus() {
      this.menus = await getMenuTree()
      return this.menus
    },
    logout() {
      this.token = ''
      this.userInfo = null
      this.menus = []
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }
})
