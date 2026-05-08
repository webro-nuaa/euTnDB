<template>
  <div class="public-layout">
    <el-container>
      <el-header class="header">
        <div class="logo" @click="$router.push('/')">
          <span class="logo-text">euTnDB</span>
          <span class="logo-subtitle">Tn in Eukaryotes</span>
        </div>
        <el-menu mode="horizontal" :ellipsis="false" router>
          <el-menu-item index="/">Home</el-menu-item>
          <el-menu-item index="/classification">Classification</el-menu-item>
          <el-menu-item index="/search">Search</el-menu-item>
          <el-menu-item index="/blast">BLAST</el-menu-item>
          <el-menu-item index="/knowledge">Knowledge</el-menu-item>
          <el-menu-item index="/help">Help</el-menu-item>
        </el-menu>
        <div class="user-actions">
          <el-button type="primary" @click="$router.push('/submit')">Submit Data</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
      <el-footer class="footer">
        <div class="footer-content">
          <p>&copy; 2024 euTnDB &mdash; Tn in Eukaryotes. All rights reserved.</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.public-layout {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 2px solid #e4e7ed;
  padding: 0 24px;
  height: 64px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  cursor: pointer;
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.logo-text {
  font-size: 26px;
  font-weight: 800;
  color: #1a73e8;
  letter-spacing: -0.5px;
}

.logo-subtitle {
  font-size: 12px;
  color: #909399;
  letter-spacing: 0.5px;
}

.header .el-menu {
  border-bottom: none;
  flex: 1;
  justify-content: center;
}

.header .el-menu .el-menu-item {
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.user-actions {
  display: flex;
  gap: 10px;
}

.main {
  min-height: calc(100vh - 130px);
  background: #f8f9fb;
}

.footer {
  text-align: center;
  color: #909399;
  background: #fff;
  border-top: 1px solid #e4e7ed;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer p {
  font-size: 13px;
}
</style>
