<template>
  <div class="admin-page">
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-icon" style="--accent: #1a73e8;">
          <el-icon :size="22"><Document /></el-icon>
        </div>
        <div>
          <h2 class="page-title">Tn Data Management</h2>
          <p class="page-desc">Manage and curate DNA transposon entries in the database</p>
        </div>
      </div>
      <div class="page-header-actions">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon> Add New Entry
        </el-button>
        <el-button type="success" @click="showImportDialog">
          <el-icon><Upload /></el-icon> Import Excel
        </el-button>
        <el-button @click="downloadTemplate">
          <el-icon><Document /></el-icon> Download Template
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon> Export
        </el-button>
      </div>
    </div>

    <el-card shadow="never" class="admin-card">
      <div class="filter-bar">
        <el-form :inline="true" :model="filter" class="filter-form">
          <el-form-item>
            <el-input v-model="filter.keyword" placeholder="Search name / family / group..." clearable @clear="handleSearch" prefix-icon="Search" style="width: 240px;" />
          </el-form-item>
          <el-form-item>
            <el-select v-model="filter.family" placeholder="Family" clearable style="width: 160px;">
              <el-option v-for="item in families" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-select v-model="filter.mge_type" placeholder="MGE Type" clearable style="width: 140px;">
              <el-option label="TE" value="TE" />
              <el-option label="MITE" value="MITE" />
              <el-option label="LARD" value="LARD" />
              <el-option label="TRIM" value="TRIM" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-select v-model="filter.status" placeholder="Status" clearable style="width: 130px;">
              <el-option label="Pending" value="pending" />
              <el-option label="Approved" value="approved" />
              <el-option label="Rejected" value="rejected" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon> Search
            </el-button>
            <el-button @click="resetFilter">Reset</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="tnList" v-loading="loading" style="width: 100%" class="styled-table" :header-cell-style="{ background: '#f8f9fb', color: '#5f6368', fontWeight: 600, fontSize: '13px' }">
        <el-table-column prop="name" label="Name" width="130">
          <template #default="{ row }">
            <span class="name-link" @click="viewDetail(row)">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="family" label="Family" width="140">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" class="family-tag">{{ row.family }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tn_group" label="Group" width="100" />
        <el-table-column prop="origin" label="Origin" min-width="160" show-overflow-tooltip />
        <el-table-column prop="length" label="Length" width="110" align="right">
          <template #default="{ row }">
            <span class="mono-text">{{ row.length?.toLocaleString() || '-' }}</span>
            <span class="unit-text"> bp</span>
          </template>
        </el-table-column>
        <el-table-column prop="mge_type" label="MGE Type" width="100">
          <template #default="{ row }">
            <el-tag size="small" effect="light" round>{{ row.mge_type || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="light" round>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="viewDetail(row)">View</el-button>
            <el-button size="small" text type="warning" @click="editTn(row)">Edit</el-button>
            <el-button size="small" text type="danger" @click="deleteTn(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="filter.page"
          v-model:page-size="filter.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          background
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? 'Edit Tn Entry' : 'Add Tn Entry'" width="900px" class="styled-dialog" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="140px" class="styled-form">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Name" prop="name">
              <el-input v-model="form.name" :disabled="isEdit" placeholder="e.g. ISLEEU-1" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Family" prop="family">
              <el-select v-model="form.family" style="width: 100%" placeholder="Select family">
                <el-option v-for="item in families" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Group" prop="tn_group">
              <el-input v-model="form.tn_group" placeholder="e.g. ISL2EU" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Accession No.">
              <el-input v-model="form.accession_number" placeholder="GCA_..." />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Origin">
              <el-input v-model="form.origin" placeholder="Species name" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="MGE Type">
              <el-select v-model="form.mge_type" style="width: 100%" placeholder="Select type" clearable>
                <el-option label="TE" value="TE" />
                <el-option label="MITE" value="MITE" />
                <el-option label="LARD" value="LARD" />
                <el-option label="TRIM" value="TRIM" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="DNA Sequence">
          <el-input v-model="form.dna_sequence" type="textarea" :rows="4" placeholder="Paste DNA sequence..." style="font-family: monospace;" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="Length">
              <el-input-number v-model="form.length" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="IR">
              <el-input v-model="form.ir" placeholder="e.g. 12/13" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="DR">
              <el-input-number v-model="form.dr" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="ORF">
              <el-input v-model="form.orf" placeholder="e.g. 447/308" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Synonyms">
              <el-input v-model="form.synonyms" placeholder="Synonyms" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Isoform">
              <el-input v-model="form.isoform" placeholder="Isoform" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Transposition">
              <el-input v-model="form.transposition" placeholder="Transposition" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>ORF1</el-divider>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="ORF1 Function">
              <el-input v-model="form.orf1_function" placeholder="e.g. Transposase" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="ORF1 Chemistry">
              <el-input v-model="form.orf1_chemistry" placeholder="e.g. DDE" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="ORF1 Begin">
              <el-input-number v-model="form.orf1_begin" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="ORF1 End">
              <el-input-number v-model="form.orf1_end" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>ORF2</el-divider>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="ORF2 Function">
              <el-input v-model="form.orf2_function" placeholder="e.g. Yqaj" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="ORF2 Chemistry">
              <el-input v-model="form.orf2_chemistry" placeholder="e.g. DDE" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="ORF2 Begin">
              <el-input-number v-model="form.orf2_begin" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="ORF2 End">
              <el-input-number v-model="form.orf2_end" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">Save</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" title="Import from Excel" width="600px" class="styled-dialog" destroy-on-close>
      <el-alert type="info" :closable="false" style="margin-bottom: 16px;">
        Upload an Excel file (.xlsx) with transposon data. Please use the <strong>Download Template</strong> button to get the correct format.
      </el-alert>
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleFileChange"
        :on-exceed="() => ElMessage.warning('Please upload only one file')"
        drag
      >
        <el-icon class="el-icon--upload" :size="40"><Upload /></el-icon>
        <div class="el-upload__text">Drop Excel file here or <em>click to upload</em></div>
        <template #tip>
          <div class="el-upload__tip">Only .xlsx / .xls files are accepted</div>
        </template>
      </el-upload>
      <div v-if="importResult" style="margin-top: 16px;">
        <el-result :icon="importResult.errors.length > 0 ? 'warning' : 'success'" :title="`Import Complete`">
          <template #sub-title>
            <p>Created: <strong>{{ importResult.created }}</strong> entries</p>
            <p>Skipped: <strong>{{ importResult.skipped }}</strong> entries</p>
            <p v-if="importResult.errors.length > 0" style="color: #ea4335;">Errors:</p>
            <ul v-if="importResult.errors.length > 0" style="text-align: left; max-height: 120px; overflow-y: auto;">
              <li v-for="err in importResult.errors" :key="err.row">Row {{ err.row }} ({{ err.name }}): {{ err.error }}</li>
            </ul>
          </template>
        </el-result>
      </div>
      <template #footer>
        <el-button @click="importDialogVisible = false; importResult = null">Close</el-button>
        <el-button type="primary" @click="handleImport" :loading="importing" :disabled="!importFile">
          Import
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Document, Plus, Download, Search, Upload } from '@element-plus/icons-vue'
import { getTnList, createTn, updateTn, deleteTn as deleteTnApi } from '@/api/tn'
import type { TnEntry, TnFilter } from '@/types/tn'
import request from '@/api/request'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const tnList = ref<TnEntry[]>([])
const total = ref(0)
const formRef = ref<FormInstance>()

const filter = reactive<any>({
  keyword: '', family: '', mge_type: '', status: '',
  page: 1, page_size: 20
})

const form = reactive<any>({
  id: 0, name: '', family: '', tn_group: '', accession_number: '',
  origin: '', mge_type: '', dna_sequence: '', length: null,
  ir: '', dr: null, orf: '', synonyms: '', isoform: '', transposition: '',
  orf1_function: '', orf1_chemistry: '', orf1_begin: null, orf1_end: null,
  orf1_length: null, orf1_strand: '+', orf1_fusion_orf: 'No',
  orf2_function: '', orf2_chemistry: '', orf2_begin: null, orf2_end: null,
  orf2_length: null, orf2_strand: '-', orf2_fusion_orf: 'No',
})

const rules: FormRules = {
  name: [{ required: true, message: 'Please enter name', trigger: 'blur' }],
  family: [{ required: true, message: 'Please select family', trigger: 'change' }],
  tn_group: [{ required: true, message: 'Please enter group', trigger: 'blur' }]
}

const families = [
  'Tc1-Mariner', 'hAT', 'MuDR', 'EnSpm', 'piggyBac', 'P', 'Merlin',
  'PIF-Harbinger', 'Transib', 'Helitron', 'Crypton'
]

onMounted(() => { loadTnList() })

async function loadTnList() {
  loading.value = true
  try {
    const params: Record<string, any> = { page: filter.page, page_size: filter.page_size }
    if (filter.keyword) params.keyword = filter.keyword
    if (filter.family) params.family = filter.family
    if (filter.mge_type) params.mge_type = filter.mge_type
    if (filter.status) params.status = filter.status
    const res = await getTnList(params as TnFilter)
    tnList.value = res.data.items
    total.value = res.data.total
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function handleSearch() { filter.page = 1; loadTnList() }

function handlePageChange() { loadTnList() }

function handleSizeChange() { filter.page = 1; loadTnList() }

function resetFilter() {
  Object.assign(filter, { keyword: '', family: '', mge_type: '', status: '', page: 1, page_size: 20 })
  loadTnList()
}

function showCreateDialog() {
  isEdit.value = false
  Object.assign(form, {
    id: 0, name: '', family: '', tn_group: '', accession_number: '',
    origin: '', mge_type: '', dna_sequence: '', length: null,
    ir: '', dr: null, orf: '', synonyms: '', isoform: '', transposition: '',
    orf1_function: '', orf1_chemistry: '', orf1_begin: null, orf1_end: null,
    orf1_length: null, orf1_strand: '+', orf1_fusion_orf: 'No',
    orf2_function: '', orf2_chemistry: '', orf2_begin: null, orf2_end: null,
    orf2_length: null, orf2_strand: '-', orf2_fusion_orf: 'No',
  })
  dialogVisible.value = true
}

function editTn(row: TnEntry) {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate()
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateTn(form.name, form)
      ElMessage.success('Updated successfully')
    } else {
      await createTn(form)
      ElMessage.success('Created successfully')
    }
    dialogVisible.value = false
    loadTnList()
  } catch (e) { console.error(e) }
  finally { submitting.value = false }
}

async function deleteTn(row: TnEntry) {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this entry?', 'Confirm', { type: 'warning' })
    await deleteTnApi(row.name)
    ElMessage.success('Deleted successfully')
    loadTnList()
  } catch (e) { console.error(e) }
}

function viewDetail(row: TnEntry) {
  window.open(`/tn/${row.name}`, '_blank')
}

function handleExport() {
  const ids = tnList.value.map((item: TnEntry) => item.name)
  request.post('/v1/export/batch', { format: 'fasta', ids }, { responseType: 'blob' })
    .then((res: any) => {
      const url = window.URL.createObjectURL(new Blob([res]))
      const a = document.createElement('a')
      a.href = url
      a.download = 'tndb_export.fasta'
      a.click()
      window.URL.revokeObjectURL(url)
    })
    .catch(() => {
      ElMessage.error('Export failed')
    })
}

function getStatusType(status: string) {
  const types: Record<string, string> = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return types[status] || 'info'
}

const importDialogVisible = ref(false)
const importing = ref(false)
const importFile = ref<File | null>(null)
const importResult = ref<{ created: number; skipped: number; errors: { row: number; name: string; error: string }[] } | null>(null)
const uploadRef = ref()

function showImportDialog() {
  importFile.value = null
  importResult.value = null
  importDialogVisible.value = true
}

function handleFileChange(file: any) {
  importFile.value = file.raw
  importResult.value = null
}

function downloadTemplate() {
  const a = document.createElement('a')
  a.href = '/api/v1/import/template'
  a.download = 'euTnDB_Import_Template.xlsx'
  a.click()
}

async function handleImport() {
  if (!importFile.value) {
    ElMessage.warning('Please select a file first')
    return
  }
  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', importFile.value)
    const res = await request.post('/v1/import/excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    importResult.value = res.data.data
    if (res.data.data.created > 0) {
      loadTnList()
    }
  } catch (e: any) {
    const msg = e?.response?.data?.detail || 'Import failed'
    ElMessage.error(msg)
  } finally {
    importing.value = false
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

.page-header-actions {
  display: flex;
  gap: 10px;
}

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

.name-link {
  color: #1a73e8;
  font-weight: 500;
  cursor: pointer;
}

.name-link:hover {
  text-decoration: underline;
}

.family-tag {
  border-radius: 10px;
  font-size: 12px;
}

.mono-text {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  color: #202124;
}

.unit-text {
  font-size: 12px;
  color: #80868b;
  margin-left: 2px;
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
