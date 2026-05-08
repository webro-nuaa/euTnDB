<template>
  <router-view />
</template>

<script setup lang="ts">
</script>

<style>
html {
  overflow-y: scroll;
}

#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #202124;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --el-color-primary: #1a73e8;
  --el-color-primary-light-3: #5ba0f0;
  --el-color-primary-light-5: #8dc1f7;
  --el-color-primary-light-7: #bdd9fa;
  --el-color-primary-light-8: #d4e6fc;
  --el-color-primary-light-9: #ebf2fe;
  --el-color-primary-dark-2: #1558b8;
}

body {
  background: #f8f9fb;
}
</style>
