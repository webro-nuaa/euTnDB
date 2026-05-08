<template>
  <div class="admin-page">
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-icon" style="--accent: #5f6368;">
          <el-icon :size="22"><Setting /></el-icon>
        </div>
        <div>
          <h2 class="page-title">System Settings</h2>
          <p class="page-desc">Configure site settings, email server, and other system options</p>
        </div>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="14">
        <el-card shadow="never" class="admin-card">
          <template #header>
            <span class="card-title">General Settings</span>
          </template>
          <el-form :model="generalForm" label-width="160px">
            <el-form-item label="Site Name">
              <el-input v-model="generalForm.site_name" />
            </el-form-item>
            <el-form-item label="Site Description">
              <el-input v-model="generalForm.site_description" type="textarea" :rows="2" />
            </el-form-item>
            <el-form-item label="Default Status">
              <el-select v-model="generalForm.default_status" style="width: 100%">
                <el-option label="Pending Review" value="pending" />
                <el-option label="Auto Approved" value="approved" />
              </el-select>
            </el-form-item>
            <el-form-item label="BLAST Service">
              <el-switch v-model="generalForm.blast_enabled" active-value="true" inactive-value="false" />
            </el-form-item>
            <el-form-item label="MineTn Service">
              <el-switch v-model="generalForm.minetn_enabled" active-value="true" inactive-value="false" />
            </el-form-item>
            <el-form-item label="Max Upload (MB)">
              <el-input-number v-model="generalForm.max_upload_size" :min="1" :max="1000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Max Download Entries">
              <el-input-number v-model="generalForm.max_download_entries" :min="1" :max="10000" style="width: 100%" />
              <div class="form-tip">Maximum entries per download request</div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveGeneral" :loading="saving">Save</el-button>
              <el-button @click="rebuildBlastDb" :loading="rebuildingBlast">Rebuild BLAST DB</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card shadow="never" class="admin-card">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">Email (SMTP) Settings</span>
              <el-tag :type="emailConfigured ? 'success' : 'danger'" size="small" effect="light" round>
                {{ emailConfigured ? 'Configured' : 'Not Configured' }}
              </el-tag>
            </div>
          </template>

          <el-alert
            v-if="!emailConfigured"
            type="warning"
            :closable="false"
            style="margin-bottom: 16px;"
          >
            Email is not configured. Download request notifications cannot be sent.
          </el-alert>

          <el-form :model="emailForm" label-width="140px" class="email-form">
            <el-form-item label="SMTP Host">
              <el-input v-model="emailForm.smtp_host" placeholder="smtp.gmail.com" />
            </el-form-item>
            <el-form-item label="SMTP Port">
              <el-input-number v-model="emailForm.smtp_port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Use SSL">
              <el-switch v-model="emailForm.smtp_use_ssl" active-value="true" inactive-value="false" />
            </el-form-item>
            <el-form-item label="Sender Email">
              <el-input v-model="emailForm.smtp_user" placeholder="your@email.com" />
            </el-form-item>
            <el-form-item label="Authorization Code">
              <el-input v-model="emailForm.smtp_password" type="password" show-password placeholder="SMTP authorization code (not login password)" />
            </el-form-item>
            <el-form-item label="Sender Name">
              <el-input v-model="emailForm.smtp_from_name" placeholder="euTnDB" />
            </el-form-item>

            <el-divider>Test Email</el-divider>
            <el-form-item label="Send Test To">
              <div style="display: flex; gap: 8px; width: 100%;">
                <el-input v-model="testEmailAddress" placeholder="test@example.com" style="flex: 1;" />
                <el-button type="success" @click="sendTestEmail" :loading="testingEmail" :disabled="!emailForm.smtp_host">
                  Send Test
                </el-button>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveEmail" :loading="savingEmail">Save Email Settings</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting } from '@element-plus/icons-vue'
import { getSystemSettings, updateSystemSettings, testEmail } from '@/api/settings'

const saving = ref(false)
const savingEmail = ref(false)
const testingEmail = ref(false)
const rebuildingBlast = ref(false)
const testEmailAddress = ref('')

const generalForm = reactive({
  site_name: 'euTnDB',
  site_description: 'DNA Transposon Database',
  default_status: 'pending',
  blast_enabled: 'true',
  minetn_enabled: 'true',
  max_upload_size: '100',
  max_download_entries: '50',
})

const emailForm = reactive({
  smtp_host: '',
  smtp_port: '465',
  smtp_user: '',
  smtp_password: '',
  smtp_from_name: 'euTnDB',
  smtp_use_ssl: 'true',
})

const emailConfigured = computed(() => !!emailForm.smtp_host && !!emailForm.smtp_user)

onMounted(() => { loadSettings() })

async function loadSettings() {
  try {
    const res = await getSystemSettings()
    const data = res.data
    Object.keys(generalForm).forEach(key => {
      if (data[key] !== undefined) (generalForm as any)[key] = data[key]
    })
    Object.keys(emailForm).forEach(key => {
      if (data[key] !== undefined) (emailForm as any)[key] = data[key]
    })
  } catch (e) { console.error(e) }
}

async function saveGeneral() {
  saving.value = true
  try {
    await updateSystemSettings({ ...generalForm })
    ElMessage.success('General settings saved')
  } catch (e) { ElMessage.error('Failed to save'); console.error(e) }
  finally { saving.value = false }
}

async function saveEmail() {
  savingEmail.value = true
  try {
    await updateSystemSettings({ ...emailForm })
    ElMessage.success('Email settings saved')
  } catch (e) { ElMessage.error('Failed to save'); console.error(e) }
  finally { savingEmail.value = false }
}

async function sendTestEmail() {
  if (!testEmailAddress.value) {
    ElMessage.warning('Please enter a test email address')
    return
  }
  if (!emailForm.smtp_host || !emailForm.smtp_user) {
    ElMessage.warning('Please fill in SMTP Host and Sender Email first')
    return
  }
  testingEmail.value = true
  try {
    await updateSystemSettings({ ...emailForm })
    await testEmail(testEmailAddress.value)
    ElMessage.success('Settings saved & test email sent! Check your inbox.')
  } catch (e: any) {
    const msg = e?.response?.data?.message || e?.response?.data?.detail || 'Failed to send test email'
    ElMessage.error(msg)
  } finally {
    testingEmail.value = false
  }
}

async function rebuildBlastDb() {
  rebuildingBlast.value = true
  try {
    const res = await fetch('/api/v1/blast/rebuild-db', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
    })
    const data = await res.json()
    if (data.code === 200) {
      ElMessage.success(data.message || 'BLAST database rebuilt')
    } else {
      ElMessage.error(data.detail || data.message || 'Failed to rebuild')
    }
  } catch (e) {
    ElMessage.error('Failed to rebuild BLAST database')
  } finally {
    rebuildingBlast.value = false
  }
}
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

.admin-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #202124;
}

.email-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #5f6368;
}

.form-tip {
  font-size: 12px;
  color: #80868b;
  margin-top: 4px;
}
</style>
