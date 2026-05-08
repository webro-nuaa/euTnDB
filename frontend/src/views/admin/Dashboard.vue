<template>
  <div class="dashboard-page">
    <el-row :gutter="20">
      <el-col :span="6">
        <div class="stat-card" style="--accent: #1a73e8;">
          <div class="stat-icon"><el-icon :size="24"><Document /></el-icon></div>
          <div class="stat-body">
            <div class="stat-number">{{ stats.tn_count || 0 }}</div>
            <div class="stat-label">Tn Entries</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="--accent: #34a853;">
          <div class="stat-icon"><el-icon :size="24"><Cherry /></el-icon></div>
          <div class="stat-body">
            <div class="stat-number">{{ stats.family_count || 0 }}</div>
            <div class="stat-label">Families</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="--accent: #fbbc04;">
          <div class="stat-icon"><el-icon :size="24"><User /></el-icon></div>
          <div class="stat-body">
            <div class="stat-number">{{ stats.pending_count || 0 }}</div>
            <div class="stat-label">Pending Review</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="--accent: #ea4335;">
          <div class="stat-icon"><el-icon :size="24"><User /></el-icon></div>
          <div class="stat-body">
            <div class="stat-number">{{ stats.user_count || 0 }}</div>
            <div class="stat-label">Users</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header><span class="card-title">Family Distribution (Top 10)</span></template>
          <div ref="pieChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header><span class="card-title">Status Distribution</span></template>
          <div ref="barChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header><span class="card-title">Recent Submissions</span></template>
          <el-table :data="recentSubmissions" style="width: 100%" size="small">
            <el-table-column prop="name" label="Name" width="120" />
            <el-table-column prop="family" label="Family" show-overflow-tooltip />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="Submitted" width="150" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header><span class="card-title">MineTn Tasks</span></template>
          <el-table :data="recentTasks" style="width: 100%" size="small">
            <el-table-column prop="task_id" label="Task ID" width="150" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="getTaskStatusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="Progress" width="140">
              <template #default="{ row }">
                <el-progress :percentage="row.progress" :stroke-width="6" />
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="Created" width="150" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Document, Cherry, User } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { get } from '@/api/request'
import type { ApiResponse } from '@/types/api'

const stats = ref<Record<string, number>>({})
const recentSubmissions = ref<any[]>([])
const recentTasks = ref<any[]>([])
const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()

onMounted(async () => {
  await Promise.all([loadStats(), loadCharts(), loadRecentData()])
})

async function loadStats() {
  try {
    const res = await get<ApiResponse<any>>('/v1/admin/stats')
    stats.value = res.data
  } catch (e) { console.error(e) }
}

async function loadCharts() {
  try {
    const [familyRes, statusRes] = await Promise.all([
      get<ApiResponse<any[]>>('/v1/stats/family'),
      get<ApiResponse<any[]>>('/v1/stats/status')
    ])
    renderPieChart(familyRes.data)
    renderBarChart(statusRes.data)
  } catch (e) { console.error(e) }
}

async function loadRecentData() {
  try {
    const [tnRes, taskRes] = await Promise.all([
      get<ApiResponse<any>>('/v1/tn', { params: { page: 1, page_size: 5 } }),
      get<ApiResponse<any[]>>('/v1/minetn')
    ])
    recentSubmissions.value = tnRes.data.items || []
    recentTasks.value = (taskRes.data || []).slice(0, 5)
  } catch (e) { console.error(e) }
}

function renderPieChart(data: any[]) {
  if (!pieChartRef.value) return
  const chart = echarts.init(pieChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left', textStyle: { fontSize: 12 } },
    series: [{
      type: 'pie', radius: ['35%', '65%'],
      data: data.map(item => ({ name: item.family, value: item.count })),
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 }
    }]
  })
}

function renderBarChart(data: any[]) {
  if (!barChartRef.value) return
  const chart = echarts.init(barChartRef.value)
  const statusColors: Record<string, string> = { approved: '#34a853', pending: '#fbbc04', rejected: '#ea4335' }
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map(item => item.status), axisLabel: { fontSize: 12 } },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: data.map(item => ({
        value: item.count,
        itemStyle: { color: statusColors[item.status] || '#1a73e8', borderRadius: [4, 4, 0, 0] }
      }))
    }],
    grid: { bottom: 30, top: 20 }
  })
}

function getStatusType(status: string) {
  const types: Record<string, string> = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return types[status] || 'info'
}

function getTaskStatusType(status: string) {
  const types: Record<string, string> = { pending: 'info', running: 'warning', completed: 'success', failed: 'danger' }
  return types[status] || 'info'
}
</script>

<style scoped>
.dashboard-page { padding: 20px; }

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-2px); }

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
  margin-right: 16px;
  flex-shrink: 0;
}

.stat-body { flex: 1; }
.stat-number { font-size: 26px; font-weight: 700; color: #202124; }
.stat-label { font-size: 13px; color: #5f6368; margin-top: 4px; }

.chart-card { border-radius: 12px; }
.card-title { font-size: 15px; font-weight: 600; color: #202124; }
</style>
