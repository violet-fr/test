/**
 * axios 请求封装
 *
 * 设计要点：
 * 1. 请求拦截器自动注入 Authorization: Bearer <token>，业务代码无需手动传 Token
 * 2. 响应拦截器统一处理后端 {code, msg, data} 格式：
 *    - code===0：返回 data 字段（业务层直接拿数据）
 *    - code!==0：弹出错误提示，Token 过期自动跳登录页
 * 3. 业务层调用只需：const data = await request.get('/xxx')，无需处理异常结构
 */
import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 axios 实例，baseURL 走 Vite 代理转发到后端 8000
const request: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

// 请求拦截器：自动携带 Token
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一处理后端响应
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    if (res.code !== 0) {
      // 业务错误：弹出后端返回的提示信息
      ElMessage.error(res.msg || '请求失败')
      // 11002=Token过期, 10002=未授权：清除登录态并跳转登录页
      if (res.code === 11002 || res.code === 10002) {
        localStorage.removeItem('access_token')
        router.push('/login')
      }
      return Promise.reject(new Error(res.msg))
    }
    // 成功：直接返回 data 字段，业务层无需再 .data
    return res.data
  },
  (error) => {
    // HTTP 层错误（网络断开、500 等）
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
