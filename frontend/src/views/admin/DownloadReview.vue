<template>
  <div class="admin-page">
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-icon" style="--accent: #34a853;">
          <el-icon :size="22"><Download /></el-icon>
        </div>
        <div>
          <h2 class="page-title">Download Review</h2>
          <p class="page-desc">Review visitor download requests and send data via email</p>
        </div>
      </div>
    </div>

    <el-row :gutter="16" class="review-stats">
      <el-col :span="8">
        <div class="mini-stat" style="--accent: #fbbc04;">
          <div class="mini-stat-icon"><el-icon :size="18"><Clock /></el-icon></div>
          <div class="mini-stat-body">
            <div class="mini-stat-number">{{ pendingTotal }}</div>
            <div class="mini-stat-label">Pending</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="mini-stat" style="--accent: #34a853;">
          <div class="mini-stat-icon"><el-icon :size="18"><Select /></el-icon></div>
          <div class="mini-stat-body">
            <div class="mini-stat-number">{{ approvedCount }}</div>
            <div class="mini-stat-label">Approved</div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="mini-stat" style="--accent: #ea4335;">
          <div class="mini-stat-icon"><el-icon :size="18"><CloseBold /></el-icon></div>
          <div class="mini-stat-body">
            <div class="mini-stat-number">{{ rejectedCount }}</div>
            <div class="mini-stat-label">Rejected</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="10">
        <el-card shadow="never" class="admin-card">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">Requests</span>
              <el-tag size="small" type="warning" effect="light" round>{{ pendingTotal }} pending</el-tag>
            </div>
          </template>
          <div v-loading="loading">
            <div v-if="!pendingList.length" class="empty-state">
              <el-empty description="No pending requests" :image-size="60" />
            </div>
            <div v-else class="request-list">
              <div
                v-for="item in pendingList"
                :key="item.id"
                class="request-item"
                :class="{ active: selectedId === item.id }"
                @click="selectRequest(item)"
              >
                <div class="request-item-top">
                  <span class="request-item-name">{{ item.requester_name || 'Anonymous' }}</span>
                  <el-tag size="small" effect="plain" round>{{ item.data_format?.toUpperCase() }}</el-tag>
                </div>
                <div class="request-item-email">{{ item.requester_email }}</div>
                <div class="request-item-bottom">
                  <span class="request-item-inst">{{ item.requester_institution || '-' }}</span>
                  <span class="request-item-date">{{ formatDate(item.created_at) }}</span>
                </div>
              </div>
            </div>
            <div v-if="pendingTotal > pendingPageSize" class="pagination-wrap">
              <el-pagination
                v-model:current-page="pendingPage"
                v-model:page-size="pendingPageSize"
                :total="pendingTotal"
                :page-sizes="[10, 20, 50]"
                layout="total, prev, next"
                @size-change="loadPending"
                @current-change="loadPending"
                background
                small
              />
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card shadow="never" class="admin-card">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">Request Detail</span>
            </div>
          </template>

          <div v-if="!selectedRequest" class="empty-state">
            <el-empty description="Select a request to view details" :image-size="80" />
          </div>

          <div v-else class="detail-content">
            <div class="detail-section">
              <h4 class="detail-section-title">Requester Information</h4>
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="Name">{{ selectedRequest.requester_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Email">{{ selectedRequest.requester_email }}</el-descriptions-item>
                <el-descriptions-item label="Institution">{{ selectedRequest.requester_institution || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Submitted">{{ formatDate(selectedRequest.created_at) }}</el-descriptions-item>
                <el-descriptions-item label="Format">
                  <el-tag size="small" effect="plain" round>{{ selectedRequest.data_format?.toUpperCase() }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="Purpose" :span="2">{{ selectedRequest.purpose || '-' }}</el-descriptions-item>
              </el-descriptions>
            </div>

            <div class="detail-section">
              <h4 class="detail-section-title">
                Requested Data
                <el-tag size="small" type="primary" effect="light" round style="margin-left: 8px;">
                  {{ parsedEntries.length }} entries
                </el-tag>
              </h4>
              <el-table :data="paginatedEntries" size="small" stripe style="width: 100%">
                <el-table-column type="index" label="#" width="50" :index="entryIndexMethod" />
                <el-table-column prop="name" label="Name" width="160">
                  <template #default="{ row }">
                    <el-link type="primary" @click="$router.push(`/tn/${row.name}`)">{{ row.name }}</el-link>
                  </template>
                </el-table-column>
                <el-table-column prop="family" label="Family" width="160">
                  <template #default="{ row }">
                    <el-tag v-if="row.family" size="small" effect="plain">{{ row.family }}</el-tag>
                    <span v-else class="text-muted">-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="origin" label="Origin" min-width="180" show-overflow-tooltip>
                  <template #default="{ row }">
                    <span>{{ row.origin || '-' }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="length" label="Length" width="120" align="right">
                  <template #default="{ row }">
                    <span v-if="row.length" class="mono-text">{{ row.length?.toLocaleString() }}</span>
                    <span v-else class="text-muted">-</span>
                  </template>
                </el-table-column>
              </el-table>
              <el-pagination
                v-if="parsedEntries.length > entryPageSize"
                v-model:current-page="entryPage"
                v-model:page-size="entryPageSize"
                :total="parsedEntries.length"
                :page-sizes="[10, 20, 50]"
                layout="total, sizes, prev, pager, next"
                background
                small
                style="margin-top: 12px; justify-content: flex-end;"
              />
            </div>

            <div class="detail-actions">
              <el-button type="success" @click="handleReview(selectedRequest, 'approve')">Approve & Send Email</el-button>
              <el-button type="danger" @click="handleReview(selectedRequest, 'reject')">Reject</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="admin-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header-row">
          <span class="card-title">Review History</span>
        </div>
      </template>
      <el-table :data="historyList" size="small" stripe style="width: 100%">
        <el-table-column prop="status" label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'approved' ? 'success' : 'danger'" size="small" effect="light" round>
              {{ row.status === 'approved' ? 'Approved' : 'Rejected' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="requester_name" label="Name" width="120">
          <template #default="{ row }">{{ row.requester_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="requester_email" label="Email" width="200" show-overflow-tooltip />
        <el-table-column prop="requested_data" label="Requested Data" min-width="200" show-overflow-tooltip />
        <el-table-column prop="data_format" label="Format" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" round>{{ row.data_format?.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="review_comment" label="Comment" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.review_comment || '-' }}</template>
        </el-table-column>
        <el-table-column prop="reviewed_at" label="Date" width="120">
          <template #default="{ row }">{{ formatDate(row.reviewed_at) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Clock, Select, CloseBold } from '@element-plus/icons-vue'
import { getPendingDownloadRequests, getDownloadRequestHistory, reviewDownloadRequest } from '@/api/download-request'
import { getTnList } from '@/api/tn'

const loading = ref(false)
const pendingList = ref<any[]>([])
const historyList = ref<any[]>([])
const pendingTotal = ref(0)
const pendingPage = ref(1)
const pendingPageSize = ref(20)
const selectedId = ref<number | null>(null)
const selectedRequest = ref<any>(null)
const parsedEntries = ref<any[]>([])
const entryPage = ref(1)
const entryPageSize = ref(10)

const paginatedEntries = computed(() => {
  const start = (entryPage.value - 1) * entryPageSize.value
  return parsedEntries.value.slice(start, start + entryPageSize.value)
})

function entryIndexMethod(index: number): number {
  return (entryPage.value - 1) * entryPageSize.value + index + 1
}

const approvedCount = computed(() => historyList.value.filter(h => h.status === 'approved').length)
const rejectedCount = computed(() => historyList.value.filter(h => h.status === 'rejected').length)

onMounted(() => { loadPending(); loadHistory() })

async function loadPending() {
  loading.value = true
  try {
    const res = await getPendingDownloadRequests({ page: pendingPage.value, page_size: pendingPageSize.value })
    pendingList.value = res.data.items
    pendingTotal.value = res.data.total
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function loadHistory() {
  try {
    const res = await getDownloadRequestHistory({ page: 1, page_size: 30 })
    historyList.value = res.data.items
  } catch (e) { console.error(e) }
}

async function selectRequest(item: any) {
  selectedId.value = item.id
  selectedRequest.value = item
  entryPage.value = 1
  await loadEntryDetails(item.requested_data)
}

async function loadEntryDetails(requestedData: string) {
  const names = requestedData.split(',').map(s => s.trim()).filter(Boolean)
  if (!names.length) {
    parsedEntries.value = names.map(name => ({ name, family: null, origin: null, length: null }))
    return
  }
  try {
    const res = await getTnList({ keyword: names.join(','), page: 1, page_size: 100 } as any)
    const allItems = res.data.items || []
    const itemMap = new Map(allItems.map((i: any) => [i.name, i]))
    parsedEntries.value = names.map(name => {
      const found = itemMap.get(name)
      return found || { name, family: null, origin: null, length: null }
    })
  } catch {
    parsedEntries.value = names.map(name => ({ name, family: null, origin: null, length: null }))
  }
}

async function handleReview(row: any, action: 'approve' | 'reject') {
  const entryCount = parsedEntries.value.length
  const actionText = action === 'approve' ? 'Approve' : 'Reject'
  try {
    const { value: comment } = await ElMessageBox.prompt(
      action === 'approve'
        ? `Approve download request from ${row.requester_name || row.requester_email}? ${entryCount} entries will be sent to ${row.requester_email}.`
        : `Reject download request from ${row.requester_name || row.requester_email}? A rejection reason is required.`,
      `${actionText} Download Request`,
      {
        confirmButtonText: actionText,
        cancelButtonText: 'Cancel',
        inputPlaceholder: action === 'approve' ? 'Comment (optional)' : 'Rejection reason (required)',
        inputValidator: action === 'reject'
          ? (val: string) => val?.trim() ? true : 'Rejection reason is required'
          : undefined,
      }
    ).catch(() => ({ value: '' }))

    if (action === 'reject' && !comment?.trim()) return

    const res = await reviewDownloadRequest(row.id, action, comment || '')
    const emailStatus = res.data.email_sent ? 'Email sent' : 'Email not configured'
    ElMessage.success(`${actionText}d! ${emailStatus}`)
    selectedRequest.value = null
    selectedId.value = null
    parsedEntries.value = []
    loadPending()
    loadHistory()
  } catch (e) { console.error(e) }
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
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

.page-title { font-size: 18px; font-weight: 700; color: #202124; margin: 0; line-height: 1.3; }
.page-desc { font-size: 13px; color: #80868b; margin: 2px 0 0; }

.review-stats { margin-bottom: 20px; }

.mini-stat {
  background: #fff;
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

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

.card-header-row { display: flex; align-items: center; gap: 8px; }
.card-title { font-size: 15px; font-weight: 600; color: #202124; }

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f1f3;
}

.empty-state { padding: 30px 0; text-align: center; }

.request-list { display: flex; flex-direction: column; gap: 8px; }

.request-item {
  padding: 12px 14px;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.request-item:hover { border-color: #c4d4f0; background: #fafcff; }
.request-item.active { border-color: #1a73e8; background: #f0f5ff; box-shadow: 0 0 0 1px #1a73e8; }

.request-item-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.request-item-name { font-size: 14px; font-weight: 600; color: #202124; }
.request-item-email { font-size: 12px; color: #5f6368; margin-bottom: 4px; }

.request-item-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.request-item-inst { font-size: 12px; color: #80868b; }
.request-item-date { font-size: 11px; color: #b0b0b0; }

.detail-content { }

.detail-section { margin-bottom: 20px; }
.detail-section:last-of-type { margin-bottom: 0; }

.detail-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #202124;
  margin: 0 0 12px;
  display: flex;
  align-items: center;
}

.detail-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #f0f1f3;
  margin-top: 20px;
}

.mono-text { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; color: #202124; }
.text-muted { color: #b0b0b0; }
</style>
