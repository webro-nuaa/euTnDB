<template>
  <div class="admin-page">
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-icon" style="--accent: #ea4335;">
          <el-icon :size="22"><Cpu /></el-icon>
        </div>
        <div>
          <h2 class="page-title">MineTn Workbench</h2>
          <p class="page-desc">Detect TIR transposons in genome sequences using MineTn</p>
        </div>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="never" class="admin-card task-create-card">
          <template #header>
            <div class="card-header-row">
              <el-icon class="card-header-icon" :size="18" color="#1a73e8"><UploadFilled /></el-icon>
              <span class="card-title">Create Analysis Task</span>
            </div>
          </template>
          <el-form :model="taskForm" label-width="140px" class="styled-form">
            <el-form-item label="Genome File">
              <el-upload
                drag
                action="/api/v1/minetn/upload"
                :on-success="handleUploadSuccess"
                :headers="uploadHeaders"
                accept=".fa,.fasta,.fna"
                :limit="1"
                class="genome-upload"
              >
                <div class="upload-inner">
                  <el-icon class="upload-icon" :size="28"><UploadFilled /></el-icon>
                  <div class="upload-text">Drop or click to upload</div>
                  <div class="upload-hint">FASTA format (.fa, .fasta, .fna)</div>
                </div>
              </el-upload>
            </el-form-item>
            <el-divider content-position="left" class="param-divider">TIR Detection Parameters</el-divider>
            <el-form-item label="Min TIR Length">
              <el-input-number v-model="taskForm.min_tir_length" :min="5" :max="100" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Max TIR Length">
              <el-input-number v-model="taskForm.max_tir_length" :min="10" :max="200" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Min Similarity">
              <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
                <el-slider v-model="taskForm.min_tir_similarity" :min="0.5" :max="1" :step="0.05" style="flex: 1;" />
                <span class="slider-value">{{ (taskForm.min_tir_similarity * 100).toFixed(0) }}%</span>
              </div>
            </el-form-item>
            <el-form-item label="Element Length">
              <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
                <el-input-number v-model="taskForm.min_element_length" :min="50" style="flex: 1;" />
                <span class="range-sep">-</span>
                <el-input-number v-model="taskForm.max_element_length" :max="50000" style="flex: 1;" />
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitTask" :loading="submitting" style="width: 100%;">
                <el-icon><VideoPlay /></el-icon> Start Analysis
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card shadow="never" class="admin-card">
          <template #header>
            <div class="card-header-row">
              <el-icon class="card-header-icon" :size="18" color="#34a853"><List /></el-icon>
              <span class="card-title">Task List</span>
              <el-tag size="small" effect="plain" round style="margin-left: 8px;">{{ tasks.length }} tasks</el-tag>
            </div>
          </template>
          <el-table :data="tasks" style="width: 100%" class="styled-table" :header-cell-style="{ background: '#f8f9fb', color: '#5f6368', fontWeight: 600, fontSize: '13px' }">
            <el-table-column prop="task_id" label="Task ID" width="180">
              <template #default="{ row }">
                <span class="mono-text">{{ row.task_id }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="genome_file" label="Genome" show-overflow-tooltip />
            <el-table-column label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small" effect="light" round>
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Progress" width="160">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.progress"
                  :stroke-width="6"
                  :status="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'exception' : ''"
                  :color="row.status === 'running' ? '#1a73e8' : undefined"
                />
              </template>
            </el-table-column>
            <el-table-column prop="detected_count" label="Detected" width="90" align="center">
              <template #default="{ row }">
                <span class="detected-count">{{ row.detected_count || 0 }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="200" align="center">
              <template #default="{ row }">
                <el-button size="small" text type="primary" @click="viewResults(row)" :disabled="row.status !== 'completed'">Results</el-button>
                <el-button size="small" text type="success" @click="importResults(row)" :disabled="row.status !== 'completed'">Import</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="resultDialogVisible" title="Detection Results" width="90%" class="styled-dialog" destroy-on-close>
      <el-table :data="currentResults" style="width: 100%" max-height="500" class="styled-table" :header-cell-style="{ background: '#f8f9fb', color: '#5f6368', fontWeight: 600, fontSize: '13px' }">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="element_id" label="Element ID" width="140">
          <template #default="{ row }"><span class="mono-text">{{ row.element_id }}</span></template>
        </el-table-column>
        <el-table-column prop="chromosome" label="Chromosome" width="110" />
        <el-table-column prop="start" label="Start" width="100" align="right">
          <template #default="{ row }"><span class="mono-text">{{ row.start?.toLocaleString() }}</span></template>
        </el-table-column>
        <el-table-column prop="end" label="End" width="100" align="right">
          <template #default="{ row }"><span class="mono-text">{{ row.end?.toLocaleString() }}</span></template>
        </el-table-column>
        <el-table-column prop="length" label="Length" width="100" align="right">
          <template #default="{ row }"><span class="mono-text">{{ row.length?.toLocaleString() }}</span> <span class="unit-text">bp</span></template>
        </el-table-column>
        <el-table-column prop="ir" label="IR" width="80" />
        <el-table-column prop="family" label="Family" width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" round>{{ row.family }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="mge_type" label="MGE Type" width="100">
          <template #default="{ row }">
            <el-tag size="small" effect="light" round>{{ row.mge_type || 'TE' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="resultDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="batchImport">Batch Import</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Cpu, UploadFilled, VideoPlay, List } from '@element-plus/icons-vue'
import { createMineTnTask, getMineTnTaskList, getMineTnResults, importMineTnResults } from '@/api/minetn'
import type { MineTnTask, MineTnResult } from '@/api/minetn'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const submitting = ref(false)
const tasks = ref<MineTnTask[]>([])
const resultDialogVisible = ref(false)
const currentResults = ref<MineTnResult[]>([])
const currentTaskId = ref('')

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${userStore.token}`
}))

const taskForm = reactive({
  genome_file: '', min_tir_length: 10, max_tir_length: 50,
  min_element_length: 50, max_element_length: 15000, min_tir_similarity: 0.8
})

onMounted(() => { loadTasks() })

async function loadTasks() {
  try { const res = await getMineTnTaskList(); tasks.value = res.data } catch (e) { console.error(e) }
}

function handleUploadSuccess(response: any) {
  taskForm.genome_file = response.data.filepath
  ElMessage.success('File uploaded successfully')
}

async function submitTask() {
  if (!taskForm.genome_file) { ElMessage.warning('Please upload a genome file first'); return }
  submitting.value = true
  try { await createMineTnTask(taskForm); ElMessage.success('Task created'); loadTasks() }
  catch (e) { console.error(e) } finally { submitting.value = false }
}

async function viewResults(task: MineTnTask) {
  currentTaskId.value = task.task_id
  try { const res = await getMineTnResults(task.task_id); currentResults.value = res.data; resultDialogVisible.value = true }
  catch (e) { console.error(e) }
}

async function importResults(task: MineTnTask) {
  try {
    const res = await getMineTnResults(task.task_id)
    const ids = res.data.map((r: MineTnResult) => r.element_id)
    await importMineTnResults(task.task_id, ids)
    ElMessage.success('Imported successfully')
  } catch (e) { console.error(e) }
}

async function batchImport() {
  const selectedIds = currentResults.value.map(r => r.element_id)
  try { await importMineTnResults(currentTaskId.value, selectedIds); ElMessage.success('Batch import successful'); resultDialogVisible.value = false }
  catch (e) { console.error(e) }
}

function getStatusType(status: string) {
  const types: Record<string, string> = { pending: 'info', running: 'warning', completed: 'success', failed: 'danger' }
  return types[status] || 'info'
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
  align-items: center;
  gap: 8px;
}

.card-header-icon {
  flex-shrink: 0;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #202124;
}

.task-create-card {
  position: sticky;
  top: 20px;
}

.genome-upload :deep(.el-upload-dragger) {
  border-radius: 10px;
  border: 2px dashed #d4d7de;
  padding: 20px;
  transition: border-color 0.3s;
}

.genome-upload :deep(.el-upload-dragger:hover) {
  border-color: #1a73e8;
}

.upload-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.upload-icon {
  color: #1a73e8;
}

.upload-text {
  font-size: 14px;
  color: #5f6368;
}

.upload-hint {
  font-size: 12px;
  color: #80868b;
}

.param-divider :deep(.el-divider__text) {
  font-size: 13px;
  font-weight: 600;
  color: #5f6368;
}

.slider-value {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  color: #1a73e8;
  font-weight: 600;
  min-width: 36px;
  text-align: right;
}

.range-sep {
  color: #80868b;
  font-size: 14px;
}

.styled-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #5f6368;
  font-size: 13px;
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

.detected-count {
  font-weight: 600;
  color: #1a73e8;
}

.similarity-cell {
  display: flex;
  align-items: center;
  gap: 8px;
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
</style>
