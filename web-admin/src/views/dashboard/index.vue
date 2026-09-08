<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in cards" :key="card.title">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon :size="40" :color="card.color"><component :is="card.icon" /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 16px">
      <template #header>欢迎使用智慧园区综合管理平台</template>
      <p>当前登录用户：{{ userStore.userInfo?.nickname }}</p>
      <p>骨架已就绪，请各模块小组参照 API 文档开发对应功能。</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const cards = [
  { title: '园区人数', value: 320, icon: 'User', color: '#409EFF' },
  { title: '今日访客', value: 15, icon: 'UserFilled', color: '#67C23A' },
  { title: '活跃告警', value: 3, icon: 'Warning', color: '#E6A23C' },
  { title: '在线设备', value: 45, icon: 'Cpu', color: '#F56C6C' }
]
</script>

<style scoped>
.stat-card { display: flex; align-items: center; gap: 16px; }
.stat-value { font-size: 28px; font-weight: bold; }
.stat-label { color: #909399; font-size: 14px; }
</style>
