import request from './request'

export interface LoginForm {
  username: string
  password: string
}

export interface LoginResult {
  access_token: string
  refresh_token: string
  token_type: string
  user: {
    id: number
    username: string
    nickname: string
    avatar: string | null
    roles: string[]
  }
}

export function login(data: LoginForm): Promise<LoginResult> {
  return request.post('/auth/login', data)
}

export function getUserInfo(): Promise<LoginResult['user']> {
  return request.get('/auth/me')
}

export interface MenuItem {
  id: number
  parent_id: number
  name: string
  path: string
  component: string | null
  icon: string | null
  sort: number
  type: number
  permission: string | null
  children: MenuItem[]
}

export function getMenuTree(): Promise<MenuItem[]> {
  return request.get('/system/menus')
}
