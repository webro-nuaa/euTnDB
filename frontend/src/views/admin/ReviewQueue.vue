<template>
  <div class="admin-page">
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-icon" style="--accent: #fbbc04;">
          <el-icon :size="22"><Finished /></el-icon>
        </div>
        <div>
          <h2 class="page-title">Review Queue</h2>
          <p class="page-desc">Review and approve submitted transposon entries</p>
        </div>
      </div>
    </div>

    <el-row :gutter="16" class="review-stats">
      <el-col :span="6">
        <div class="mini-stat" style="--accent: #fbbc04;">
          <div class="mini-stat-icon"><el-icon :size="18"><Clock /></el-icon></div>
          <div class="mini-stat-body">
            <div class="mini-stat-number">{{ total }}</div>
            <div class="mini-stat-label">Pending</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="mini-stat" style="--accent: #34a853;">
          <div class="mini-stat-icon"><el-icon :size="18"><Select /></el-icon></div>
          <div class="mini-stat-body">
            <div class="mini-stat-number">{{ approvedCount }}</div>
            <div class="mini-stat-label">Approved</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="mini-stat" style="--accent: #ea4335;">
          <div class="mini-stat-icon"><el-icon :size="18"><CloseBold /></el-icon></div>
          <div class="mini-stat-body">
            <div class="mini-stat-number">{{ rejectedCount }}</div>
            <div class="mini-stat-label">Rejected</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="mini-stat" style="--accent: #1a73e8;">
          <div class="mini-stat-icon"><el-icon :size="18"><Document /></el-icon></div>
          <div class="mini-stat-body">
            <div class="mini-stat-number">{{ historyList.length }}</div>
            <div class="mini-stat-label">Total Reviewed</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card shadow="never" class="admin-card">
          <template #header>
            <div class="card-header-row">
              <el-icon class="card-header-icon" :size="18" color="#fbbc04"><Clock /></el-icon>
              <span class="card-title">Pending Review</span>
              <el-tag size="small" type="warning" effect="light" round style="margin-left: 8px;">{{ total }} entries</el-tag>
            </div>
          </template>
          <el-table :data="pendingList" v-loading="loading" style="width: 100%" class="styled-table" :header-cell-style="{ background: '#f8f9fb', color: '#5f6368', fontWeight: 600, fontSize: '13px' }">
            <el-table-column prop="name" label="Name" width="130">
              <template #default="{ row }">
                <el-link type="primary" :underline="false" @click="viewDetail(row)" class="name-link">{{ row.name }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="family" label="Family" width="130">
              <template #default="{ row }">
                <el-tag size="small" effect="plain" round>{{ row.family }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="origin" label="Origin" min-width="160" show-overflow-tooltip />
            <el-table-column prop="length" label="Length" width="100" align="right">
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
            <el-table-column prop="created_at" label="Submitted" width="140" />
            <el-table-column label="Actions" width="200" fixed="right" align="center">
              <template #default="{ row }">
                <el-button size="small" type="success" round @click="handleReview(row, 'approve')">
                  <el-icon><Select /></el-icon> Approve
                </el-button>
                <el-button size="small" type="danger" round @click="handleReview(row, 'reject')">
                  <el-icon><CloseBold /></el-icon> Reject
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-wrap">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              @size-change="loadPending"
              @current-change="loadPending"
              background
            />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="admin-card">
          <template #header>
            <div class="card-header-row">
              <el-icon class="card-header-icon" :size="18" color="#1a73e8"><Document /></el-icon>
              <span class="card-title">Review History</span>
            </div>
          </template>
          <div class="history-list">
            <div v-for="item in historyList" :key="item.id" class="history-item">
              <div class="history-action">
                <el-tag :type="item.action === 'approve' ? 'success' : 'danger'" size="small" effect="light" round>
                  {{ item.action === 'approve' ? 'Approved' : 'Rejected' }}
                </el-tag>
              </div>
              <div class="history-content">
                <div class="history-comment">{{ item.comment || 'No comment' }}</div>
                <div class="history-time">{{ item.created_at }}</div>
              </div>
            </div>
            <el-empty v-if="!historyList.length" description="No review history" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Finished, Clock, Select, CloseBold, Document } from '@element-plus/icons-vue'
import { getPendingReviews, reviewTn, getReviewHistory } from '@/api/review'

const loading = ref(false)
const pendingList = ref<any[]>([])
const historyList = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const approvedCount = computed(() => historyList.value.filter(h => h.action === 'approve').length)
const rejectedCount = computed(() => historyList.value.filter(h => h.action === 'reject').length)

onMounted(() => { loadPending(); loadHistory() })

async function loadPending() {
  loading.value = true
  try { const res = await getPendingReviews({ page: page.value, page_size: pageSize.value }); pendingList.value = res.data.items; total.value = res.data.total }
  catch (e) { console.error(e) } finally { loading.value = false }
}

async function loadHistory() {
  try { const res = await getReviewHistory({ page: 1, page_size: 20 }); historyList.value = res.data.items }
  catch (e) { console.error(e) }
}

async function handleReview(row: any, action: 'approve' | 'reject') {
  const actionText = action === 'approve' ? 'Approve' : 'Reject'
  try {
    const { value: comment } = await ElMessageBox.prompt(
      `Are you sure you want to ${actionText.toLowerCase()} entry ${row.name}?`,
      'Review Action',
      { confirmButtonText: actionText, cancelButtonText: 'Cancel', inputPlaceholder: 'Comment (optional)' }
    ).catch(() => ({ value: '' }))
    await reviewTn(row.name, action, comment || '')
    ElMessage.success(`${actionText}d successfully`)
    loadPending(); loadHistory()
  } catch (e) { console.error(e) }
}

function viewDetail(row: any) { window.open(`/tn/${row.name}`, '_blank') }
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

.review-stats {
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

.card-header-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header-icon { flex-shrink: 0; }
.card-title { font-size: 15px; font-weight: 600; color: #202124; }

.name-link {
  font-weight: 500;
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

.history-list {
  max-height: 500px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
}

.history-item:last-child { border-bottom: none; }

.history-action { flex-shrink: 0; padding-top: 2px; }

.history-content { flex: 1; min-width: 0; }

.history-comment {
  font-size: 13px;
  color: #5f6368;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-time {
  font-size: 12px;
  color: #80868b;
  margin-top: 4px;
}
</style>
