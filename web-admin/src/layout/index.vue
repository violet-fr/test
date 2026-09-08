<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="aside">
      <div class="logo">智慧园区</div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#001529"
        text-color="#fff"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        <el-sub-menu
          v-for="menu in userStore.menus"
          :key="menu.id"
          :index="String(menu.id)"
        >
          <template #title>
            <el-icon><component :is="menu.icon || 'Menu'" /></el-icon>
            <span>{{ menu.name }}</span>
          </template>
          <el-menu-item
            v-for="child in menu.children"
            :key="child.id"
            :index="`/${menu.path}/${child.path}`"
          >
            {{ child.name }}
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">智慧园区综合管理平台</div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              {{ userStore.userInfo?.nickname || '用户' }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container { height: 100vh; }
.aside { background: #001529; overflow-y: auto; }
.logo {
  height: 60px; line-height: 60px; text-align: center;
  color: #fff; font-size: 18px; font-weight: bold;
  border-bottom: 1px solid #1f2d3d;
}
.header {
  background: #fff; display: flex; align-items: center;
  justify-content: space-between; padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}
.header-left { font-size: 16px; font-weight: bold; }
.user-info { cursor: pointer; display: flex; align-items: center; gap: 4px; }
.main { background: #f0f2f5; padding: 16px; }
</style>
