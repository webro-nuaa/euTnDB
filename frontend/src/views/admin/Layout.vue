<template>
  <div class="admin-layout">
    <el-container :style="{ marginLeft: sidebarCollapsed ? '64px' : '220px' }" class="main-container">
      <el-aside :width="sidebarCollapsed ? '64px' : '220px'" class="sidebar">
        <div class="logo">
          <span v-if="!sidebarCollapsed" class="logo-full">euTnDB</span>
          <span v-else class="logo-short">Tn</span>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          :collapse="sidebarCollapsed"
          background-color="#1e2a3a"
          text-color="#8c9db5"
          active-text-color="#ffffff"
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>Dashboard</span>
          </el-menu-item>
          <el-menu-item index="/admin/tn">
            <el-icon><Document /></el-icon>
            <span>Tn Data</span>
          </el-menu-item>
          <el-menu-item index="/admin/minetn">
            <el-icon><Cpu /></el-icon>
            <span>MineTn</span>
          </el-menu-item>
          <el-menu-item index="/admin/review">
            <el-icon><Finished /></el-icon>
            <span>Review</span>
          </el-menu-item>
          <el-menu-item index="/admin/download-review">
            <el-icon><Download /></el-icon>
            <span>Download Review</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>Users</span>
          </el-menu-item>
          <el-menu-item index="/admin/settings">
            <el-icon><Setting /></el-icon>
            <span>Settings</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-button text @click="toggleSidebar" class="collapse-btn">
              <el-icon :size="18"><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
            </el-button>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/admin' }">Home</el-breadcrumb-item>
              <el-breadcrumb-item>{{ $route.meta.title }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-dropdown>
              <span class="user-info">
                <el-avatar :size="30" class="user-avatar">{{ userStore.user?.username?.charAt(0)?.toUpperCase() }}</el-avatar>
                <span class="username">{{ userStore.user?.username }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/')">Back to Site</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">Sign Out</el-dropdown-item>
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { DataAnalysis, Document, Cpu, Finished, Download, User, Setting, Fold, Expand } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const sidebarCollapsed = computed(() => appStore.sidebarCollapsed)

onMounted(() => {
  if (userStore.isLoggedIn && !userStore.user) {
    userStore.fetchUser()
  }
})

function toggleSidebar() {
  appStore.toggleSidebar()
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
}

.sidebar {
  background: #1e2a3a;
  transition: width 0.3s ease;
  overflow-x: hidden;
  overflow-y: auto;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.sidebar .logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.logo-full {
  color: #fff;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 1px;
}

.logo-short {
  color: #fff;
  font-size: 18px;
  font-weight: 800;
}

.sidebar .el-menu {
  border-right: none;
  flex: 1;
  overflow-y: auto;
}

.sidebar .el-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
  margin: 2px 8px;
  border-radius: 6px;
}

.sidebar .el-menu .el-menu-item.is-active {
  background: #1a73e8 !important;
  color: #fff !important;
}

.sidebar .el-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.06) !important;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #eef0f5;
  padding: 0 20px;
  height: 56px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.collapse-btn {
  padding: 4px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.user-info:hover {
  background: #f5f7fa;
}

.user-avatar {
  background: #1a73e8;
  color: #fff;
  font-size: 13px;
}

.username {
  color: #5f6368;
  font-size: 14px;
}

.main-container {
  transition: margin-left 0.3s ease;
  min-height: 100vh;
}

.main {
  background: #f5f7fa;
  overflow-y: auto;
}
</style>
