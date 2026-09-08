import request from './request'

export interface LoginForm {
  username: string
  password: string
}

export function login(data: LoginForm) {
  return request.post('/auth/login', data)
}

export function getUserInfo() {
  return request.get('/auth/me')
}

export function getMenuTree() {
  return request.get('/system/menus')
}
