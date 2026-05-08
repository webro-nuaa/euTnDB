<template>
  <div class="admin-page">
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-icon" style="--accent: #34a853;">
          <el-icon :size="22"><User /></el-icon>
        </div>
        <div>
          <h2 class="page-title">User Management</h2>
          <p class="page-desc">Manage admin accounts</p>
        </div>
      </div>
      <div class="page-header-actions">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon> Add User
        </el-button>
      </div>
    </div>

    <el-row :gutter="16" class="user-stats">
      <el-col :span="8">
        <div class="mini-stat" style="--accent: #1a73e8;">
          <div class="mini-stat-icon"><el-icon :size="18"><User /></el-icon></div>
          <div class="mini-stat-body">
            <div class="mini-stat-number">{{ total }}</div>
            <div class="mini-stat-label">Total Users</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="mini-stat" style="--accent: #34a853;">
          <div class="mini-stat-icon"><el-icon :size="18"><Select /></el-icon></div>
          <div class="mini-stat-body">
            <div class="mini-stat-number">{{ activeCount }}</div>
            <div class="mini-stat-label">Active</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="mini-stat" style="--accent: #ea4335;">
          <div class="mini-stat-icon"><el-icon :size="18"><CloseBold /></el-icon></div>
          <div class="mini-stat-body">
            <div class="mini-stat-number">{{ disabledCount }}</div>
            <div class="mini-stat-label">Disabled</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-card shadow="never" class="admin-card">
      <div class="filter-bar">
        <el-form :inline="true" :model="filter" class="filter-form">
          <el-form-item>
            <el-input v-model="filter.keyword" placeholder="Search username / email..." clearable @clear="handleSearch" prefix-icon="Search" style="width: 260px;" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon> Search
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="userList" v-loading="loading" style="width: 100%" class="styled-table" :header-cell-style="{ background: '#f8f9fb', color: '#5f6368', fontWeight: 600, fontSize: '13px' }">
        <el-table-column prop="username" label="Username" width="130">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="28" class="user-mini-avatar">{{ row.username?.charAt(0)?.toUpperCase() }}</el-avatar>
              <span class="user-name">{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="Email" min-width="200" />
        <el-table-column prop="role" label="Role" width="110">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small" effect="light" round>
              {{ row.role === 'admin' ? 'Admin' : 'User' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="institution" label="Institution" show-overflow-tooltip min-width="150" />
        <el-table-column prop="is_active" label="Status" width="100">
          <template #default="{ row }">
            <div class="status-cell">
              <span class="status-dot" :class="row.is_active ? 'active' : 'disabled'"></span>
              <span>{{ row.is_active ? 'Active' : 'Disabled' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Created" width="140" />
        <el-table-column label="Actions" width="250" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="editUser(row)">Edit</el-button>
            <el-button size="small" text :type="row.is_active ? 'warning' : 'success'" @click="toggleActive(row)">
              {{ row.is_active ? 'Disable' : 'Enable' }}
            </el-button>
            <el-button size="small" text type="danger" @click="handleDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination v-model:current-page="filter.page" v-model:page-size="filter.page_size" :total="total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="loadList" @current-change="loadList" background />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? 'Edit User' : 'Add User'" width="500px" class="styled-dialog" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px" class="styled-form">
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="Enter username" />
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" placeholder="Enter email address" />
        </el-form-item>
        <el-form-item label="Password" :prop="isEdit ? '' : 'password'">
          <el-input v-model="form.password" type="password" show-password :placeholder="isEdit ? 'Leave empty to keep' : 'Enter password'" />
        </el-form-item>
        <el-form-item label="Role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="Admin" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="Institution">
          <el-input v-model="form.institution" placeholder="e.g. University of Oxford" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Plus, Search, Select, CloseBold } from '@element-plus/icons-vue'
import { getUserList, createUser, updateUser, deleteUser } from '@/api/userAdmin'
import type { User as UserType } from '@/types/user'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const userList = ref<UserType[]>([])
const total = ref(0)
const formRef = ref<FormInstance>()
const filter = reactive({ keyword: '', page: 1, page_size: 20 })
const form = reactive({ id: 0, username: '', email: '', password: '', role: 'admin', institution: '' })
const rules: FormRules = { username: [{ required: true, message: 'Required', trigger: 'blur' }], email: [{ required: true, message: 'Required', trigger: 'blur' }], password: [{ required: true, message: 'Required', trigger: 'blur' }] }

const activeCount = computed(() => userList.value.filter(u => u.is_active).length)
const disabledCount = computed(() => userList.value.filter(u => !u.is_active).length)

onMounted(() => { loadList() })

async function loadList() {
  loading.value = true
  try { const res = await getUserList(filter); userList.value = res.data.items; total.value = res.data.total }
  catch (e) { console.error(e) } finally { loading.value = false }
}

function handleSearch() { filter.page = 1; loadList() }

function showCreateDialog() { isEdit.value = false; Object.assign(form, { id: 0, username: '', email: '', password: '', role: 'admin', institution: '' }); dialogVisible.value = true }

function editUser(row: UserType) { isEdit.value = true; Object.assign(form, { id: row.id, username: row.username, email: row.email, password: '', role: row.role, institution: row.institution || '' }); dialogVisible.value = true }

async function submitForm() {
  if (!formRef.value) return; await formRef.value.validate()
  submitting.value = true
  try {
    if (isEdit.value) { const data: Record<string, any> = { email: form.email, role: form.role, institution: form.institution }; if (form.password) data.password = form.password; await updateUser(form.id, data); ElMessage.success('Updated') }
    else { await createUser({ username: form.username, email: form.email, password: form.password, role: form.role, institution: form.institution || undefined }); ElMessage.success('Created') }
    dialogVisible.value = false; loadList()
  } catch (e) { console.error(e) } finally { submitting.value = false }
}

async function toggleActive(row: UserType) { try { await updateUser(row.id, { is_active: !row.is_active }); ElMessage.success(row.is_active ? 'Disabled' : 'Enabled'); loadList() } catch (e) { console.error(e) } }

async function handleDelete(row: UserType) { try { await ElMessageBox.confirm('Delete this user?', 'Confirm', { type: 'warning' }); await deleteUser(row.id); ElMessage.success('Deleted'); loadList() } catch (e) { console.error(e) } }
</script>

<style scoped>
.admin-page { padding: 20px; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.page-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
}

.page-title {
  font-size: 18px;
  font-weight: 700;
  color: #202124;
  margin: 0;
  line-height: 1.3;
}

.page-desc {
  font-size: 13px;
  color: #80868b;
  margin: 2px 0 0;
}

.page-header-actions {
  display: flex;
  gap: 10px;
}

.user-stats {
  margin-bottom: 20px;
}

.mini-stat {
  background: #fff;
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s;
}

.mini-stat:hover { transform: translateY(-1px); }

.mini-stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
  margin-right: 12px;
  flex-shrink: 0;
}

.mini-stat-body { flex: 1; }
.mini-stat-number { font-size: 20px; font-weight: 700; color: #202124; }
.mini-stat-label { font-size: 12px; color: #80868b; margin-top: 2px; }

.admin-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.filter-bar {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f1f3;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-mini-avatar {
  background: #1a73e8;
  color: #fff;
  font-size: 12px;
  flex-shrink: 0;
}

.user-name {
  font-weight: 500;
  color: #202124;
}

.status-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.status-dot.active {
  background: #34a853;
  box-shadow: 0 0 4px rgba(52, 168, 83, 0.4);
}

.status-dot.disabled {
  background: #ea4335;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f1f3;
}

.styled-table :deep(.el-table__row:hover > td) {
  background: #f8faff !important;
}

.styled-dialog :deep(.el-dialog) {
  border-radius: 12px;
}

.styled-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #f0f1f3;
  padding-bottom: 16px;
}

.styled-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid #f0f1f3;
  padding-top: 16px;
}

.styled-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #5f6368;
}
</style>
