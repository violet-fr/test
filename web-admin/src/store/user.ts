import { defineStore } from 'pinia'
import { login as apiLogin, getUserInfo, getMenuTree } from '@/api/auth'

interface UserState {
  token: string
  userInfo: any
  menus: any[]
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('access_token') || '',
    userInfo: null,
    menus: []
  }),
  actions: {
    async login(username: string, password: string) {
      const res: any = await apiLogin({ username, password })
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
