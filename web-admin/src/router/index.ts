/**
 * 路由配置 + 全局路由守卫
 *
 * 权限控制策略：
 * 1. 静态路由：登录页（无需鉴权）、工作台（需鉴权）
 * 2. 动态路由：各业务模块页面由对应小组开发后，在 children 数组中注册
 * 3. 路由守卫：未登录跳登录页；首次进入拉取用户信息和菜单（用于侧边栏渲染）
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '工作台', icon: 'HomeFilled' }
      }
      // 动态路由：各模块页面由各小组开发后在此注册
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫：鉴权 + 用户信息预加载
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 登录页免鉴权
  if (to.meta.requiresAuth === false) {
    return next()
  }

  // 无 Token -> 跳登录
  if (!userStore.token) {
    return next('/login')
  }

  // 有 Token 但无用户信息 -> 拉取用户信息和菜单（页面刷新后恢复状态）
  if (!userStore.userInfo) {
    try {
      await userStore.fetchUserInfo()
      await userStore.fetchMenus()
    } catch {
      // 拉取失败（如 Token 过期）-> 清除登录态跳登录
      userStore.logout()
      return next('/login')
    }
  }

  next()
})

export default router
