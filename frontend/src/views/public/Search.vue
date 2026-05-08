<template>
  <div class="search-page">
    <el-card shadow="never" class="page-card">
      <template #header>
        <span class="page-title">Advanced Search</span>
      </template>

      <el-form :model="searchForm" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Keyword">
              <el-input v-model="searchForm.keyword" placeholder="Name, family, group, origin..." />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Family">
              <el-select v-model="searchForm.family" placeholder="All" clearable style="width: 100%">
                <el-option v-for="item in families" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Origin">
              <el-input v-model="searchForm.origin" placeholder="Species name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="MGE Type">
              <el-select v-model="searchForm.mge_type" placeholder="All" clearable style="width: 100%">
                <el-option label="TE" value="TE" />
                <el-option label="MITE" value="MITE" />
                <el-option label="LARD" value="LARD" />
                <el-option label="TRIM" value="TRIM" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Sequence Length">
              <el-col :span="11">
                <el-input-number v-model="searchForm.minLength" :min="0" placeholder="Min" style="width: 100%" />
              </el-col>
              <el-col :span="2" class="text-center">-</el-col>
              <el-col :span="11">
                <el-input-number v-model="searchForm.maxLength" :min="0" placeholder="Max" style="width: 100%" />
              </el-col>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Group">
              <el-input v-model="searchForm.tn_group" placeholder="Group name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetForm">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="page-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>Search Results ({{ total }} entries)</span>
          <div class="card-header-actions">
            <el-tag v-if="selectedRows.length" type="success" effect="plain" round style="margin-right: 8px;">
              {{ selectedRows.length }} selected
            </el-tag>
            <el-button type="success" size="small" @click="openDownloadDialog" :disabled="!selectedRows.length">
              Batch Download
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        ref="tableRef"
        :data="results"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="45" />
        <el-table-column prop="name" label="Name" width="140">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/tn/${row.name}`)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="family" label="Family" width="160">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.family }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tn_group" label="Group" width="120" />
        <el-table-column prop="origin" label="Origin" min-width="180" show-overflow-tooltip />
        <el-table-column prop="length" label="Length" width="120" align="right">
          <template #default="{ row }">
            <span class="mono-text">{{ row.length?.toLocaleString() || '-' }}</span>
            <span class="unit-text"> bp</span>
          </template>
        </el-table-column>
        <el-table-column prop="accession_number" label="Accession" width="180" show-overflow-tooltip />
      </el-table>

      <el-pagination
        v-model:current-page="searchForm.page"
      v-model:page-size="searchForm.page_size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <el-dialog
      v-model="downloadDialogVisible"
      title="Download Request"
      width="560px"
      :close-on-click-modal="false"
    >
      <el-alert type="info" :closable="false" style="margin-bottom: 16px;">
        You selected <strong>{{ selectedRows.length }}</strong> entries. Please fill in your information to submit a download request.
        An administrator will review and send the data to your email.
      </el-alert>
      <el-alert v-if="selectedRows.length > maxDownloadEntries" type="error" :closable="false" style="margin-bottom: 16px;">
        You selected too many entries ({{ selectedRows.length }}). Maximum allowed is {{ maxDownloadEntries }}. Please reduce your selection.
      </el-alert>

      <el-form :model="downloadForm" :rules="downloadRules" ref="downloadFormRef" label-width="140px">
        <el-form-item label="Email" prop="requester_email">
          <el-input v-model="downloadForm.requester_email" placeholder="your@email.com" />
        </el-form-item>
        <el-form-item label="Name">
          <el-input v-model="downloadForm.requester_name" placeholder="Your name" />
        </el-form-item>
        <el-form-item label="Institution">
          <el-input v-model="downloadForm.requester_institution" placeholder="University / Organization" />
        </el-form-item>
        <el-form-item label="Export Format">
          <el-radio-group v-model="downloadForm.data_format">
            <el-radio-button value="fasta">FASTA</el-radio-button>
            <el-radio-button value="embl">EMBL</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Purpose of Use">
          <el-input v-model="downloadForm.purpose" type="textarea" :rows="3" placeholder="Briefly describe how you plan to use the data" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="downloadDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitDownloadRequest" :loading="downloadSubmitting" :disabled="selectedRows.length > maxDownloadEntries">Submit Request</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { searchTn } from '@/api/search'
import { submitDownloadRequest as apiSubmitDownloadRequest } from '@/api/download-request'
import { getSystemSettings } from '@/api/settings'
import type { TnEntry } from '@/types/tn'

const route = useRoute()
const loading = ref(false)
const results = ref<TnEntry[]>([])
const total = ref(0)
const selectedRows = ref<TnEntry[]>([])
const tableRef = ref()
const maxDownloadEntries = ref(50)

const searchForm = reactive({
  keyword: '',
  family: '',
  tn_group: '',
  origin: '',
  mge_type: '' as string | undefined,
  minLength: undefined as number | undefined,
  maxLength: undefined as number | undefined,
  page: 1,
  page_size: 20
})

const families = [
  'Tc1-Mariner', 'hAT', 'MuDR', 'EnSpm', 'piggyBac', 'P', 'Merlin',
  'PIF-Harbinger', 'Transib', 'Helitron', 'Crypton'
]

const downloadDialogVisible = ref(false)
const downloadSubmitting = ref(false)
const downloadFormRef = ref<FormInstance>()

const downloadForm = reactive({
  requester_email: '',
  requester_name: '',
  requester_institution: '',
  data_format: 'fasta',
  purpose: '',
})

const downloadRules: FormRules = {
  requester_email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email', trigger: 'blur' }
  ],
}

onMounted(() => {
  if (route.query.keyword) {
    searchForm.keyword = route.query.keyword as string
  }
  if (route.query.family) {
    searchForm.family = route.query.family as string
  }
  if (route.query.keyword || route.query.family || route.query.origin || route.query.tn_group) {
    handleSearch()
  }
  loadMaxDownloadLimit()
})

async function loadMaxDownloadLimit() {
  try {
    const res = await getSystemSettings()
    const val = res.data?.max_download_entries
    if (val) maxDownloadEntries.value = parseInt(val, 10) || 50
  } catch { /* ignore */ }
}

async function handleSearch() {
  searchForm.page = 1
  await doSearch()
}

function handlePageChange() { doSearch() }

function handleSizeChange() { searchForm.page = 1; doSearch() }

async function doSearch() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: searchForm.page,
    page_size: searchForm.page_size,
    }
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.family) params.family = searchForm.family
    if (searchForm.tn_group) params.tn_group = searchForm.tn_group
    if (searchForm.origin) params.origin = searchForm.origin
    if (searchForm.mge_type) params.mge_type = searchForm.mge_type
    if (searchForm.minLength != null) params.min_length = searchForm.minLength
    if (searchForm.maxLength != null) params.max_length = searchForm.maxLength

    const res = await searchTn(params as any)
    results.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(searchForm, {
    keyword: '', family: '', tn_group: '', origin: '', mge_type: undefined,
    minLength: undefined, maxLength: undefined,
    page: 1, page_size: 20
  })
  results.value = []
  total.value = 0
}

function handleSelectionChange(rows: TnEntry[]) {
  selectedRows.value = rows
}

function openDownloadDialog() {
  if (!selectedRows.value.length) {
    ElMessage.warning('Please select at least one entry')
    return
  }
  downloadFormRef.value?.resetFields()
  Object.assign(downloadForm, {
    requester_email: '', requester_name: '', requester_institution: '',
    data_format: 'fasta', purpose: '',
  })
  downloadDialogVisible.value = true
}

async function submitDownloadRequest() {
  if (!downloadFormRef.value) return
  await downloadFormRef.value.validate()

  const requestedData = selectedRows.value.map(r => r.name).join(', ')

  downloadSubmitting.value = true
  try {
    await apiSubmitDownloadRequest({
      requester_email: downloadForm.requester_email,
      requester_name: downloadForm.requester_name || undefined,
      requester_institution: downloadForm.requester_institution || undefined,
      requested_data: requestedData,
      data_format: downloadForm.data_format,
      purpose: downloadForm.purpose || undefined,
    })
    ElMessage.success('Request submitted! An administrator will review and send the data to your email.')
    downloadDialogVisible.value = false
  } catch (e) {
    console.error(e)
    ElMessage.error('Failed to submit request')
  } finally {
    downloadSubmitting.value = false
  }
}
</script>

<style scoped>
.search-page { padding: 20px; }
.page-card { border-radius: 12px; }
.page-title { font-size: 18px; font-weight: 600; color: #202124; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header-actions { display: flex; align-items: center; }
.text-center { text-align: center; line-height: 32px; }
.mono-text { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; color: #202124; }
.unit-text { font-size: 12px; color: #80868b; margin-left: 2px; }
</style>
