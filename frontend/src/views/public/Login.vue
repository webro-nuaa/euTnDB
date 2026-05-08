<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1>euTnDB</h1>
        <p>Admin Login</p>
      </div>
      
      <el-card shadow="never" class="login-card">
        <el-form :model="loginForm" :rules="rules" ref="formRef" label-width="0">
          <el-form-item prop="username">
            <el-input v-model="loginForm.username" placeholder="Username" size="large" prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="loginForm.password" type="password" placeholder="Password" size="large" prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleLogin" :loading="loading" size="large" style="width: 100%">
              Sign In
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)
const formRef = ref<FormInstance>()

const loginForm = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate()
  
  loading.value = true
  try {
    await userStore.login(loginForm.username, loginForm.password)
    ElMessage.success('Login successful')
    const redirect = (route.query.redirect as string) || '/admin'
    router.push(redirect)
  } catch (e) {
    ElMessage.error('Login failed, please check your credentials')
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
}

.login-container {
  width: 400px;
}

.login-header {
  text-align: center;
  color: #fff;
  margin-bottom: 24px;
}

.login-header h1 {
  font-size: 36px;
  font-weight: 800;
  margin: 0;
  letter-spacing: 2px;
}

.login-header p {
  font-size: 14px;
  opacity: 0.85;
  margin: 8px 0 0;
}

.login-card {
  border-radius: 12px;
  padding: 20px;
}
</style>
