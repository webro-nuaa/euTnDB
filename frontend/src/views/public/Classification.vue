<template>
  <div class="classification-page">
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="page-header">
          <span class="page-title">Classification Browser</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="Search classification..."
              prefix-icon="Search"
              clearable
              style="width: 260px;"
              @input="onSearchInput"
            />
            <el-button size="small" @click="resetView" title="Reset View">Reset</el-button>
          </div>
        </div>
      </template>

      <el-alert type="info" :closable="false" style="margin-bottom: 16px;">
        Classification based on the Dfam/Wicker et al. (2007) unified system. Click a sector to drill down, click the center to go back. Hover for details.
      </el-alert>

      <div v-if="loadError" class="error-msg">
        <el-empty description="Failed to load classification data" />
      </div>
      <div v-else class="main-layout">
        <div class="chart-col">
          <div class="sunburst-wrapper">
            <div class="sunburst-container" ref="chartContainer"></div>
            <div
              class="center-overlay"
              :class="{ clickable: !isTopLevel }"
              @click="onCenterClick"
            >
              <span class="center-text" :class="{ active: !isTopLevel }">{{ centerLabel }}</span>
            </div>
          </div>
        </div>
        <div class="sf-col">
          <el-card shadow="never" class="sf-card-wrap" v-if="superfamilies.length > 0">
            <template #header>
              <span class="sf-heading">Superfamilies</span>
            </template>
            <div class="sf-grid">
              <div
                v-for="sf in pagedSuperfamilies"
                :key="sf.name"
                class="sf-card"
                @click="goToSearch(sf.name)"
              >
                <div class="sf-name">{{ sf.name }}</div>
                <div class="sf-meta">
                  <span v-if="sf.typical_tir" class="sf-tag">TIR: {{ sf.typical_tir }}</span>
                  <span v-if="sf.typical_tsd" class="sf-tag">TSD: {{ sf.typical_tsd }}</span>
                  <el-tag size="small" type="info" round>{{ sf.count }}</el-tag>
                </div>
              </div>
            </div>
            <div class="sf-pagination" v-if="superfamilies.length > sfPageSize">
              <el-pagination
                small
                layout="prev, pager, next"
                :total="superfamilies.length"
                :page-size="sfPageSize"
                v-model:current-page="sfCurrentPage"
              />
            </div>
          </el-card>
        </div>
      </div>

      <div v-if="selectedInfo" class="detail-panel">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="Name">{{ selectedInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="Code" v-if="selectedInfo.code">{{ selectedInfo.code }}</el-descriptions-item>
          <el-descriptions-item label="Aliases" v-if="selectedInfo.aliases">{{ selectedInfo.aliases }}</el-descriptions-item>
          <el-descriptions-item label="Entries">{{ selectedInfo.count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="TIR" v-if="selectedInfo.typical_tir">{{ selectedInfo.typical_tir }}</el-descriptions-item>
          <el-descriptions-item label="TSD" v-if="selectedInfo.typical_tsd">{{ selectedInfo.typical_tsd }}</el-descriptions-item>
        </el-descriptions>
        <div style="margin-top: 10px; display: flex; gap: 8px;">
          <el-button
            type="primary"
            size="small"
            @click="goToSearch(selectedInfo.name)"
          >
            Search {{ selectedInfo.name }}
          </el-button>
          <el-button
            v-if="selectedInfo.children && selectedInfo.children.length > 0"
            size="small"
            @click="drillDown(selectedInfo)"
          >
            Drill down ({{ selectedInfo.children.length }} subcategories)
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'

const router = useRouter()
const chartContainer = ref<HTMLElement | null>(null)
const searchKeyword = ref('')
const selectedInfo = ref<any>(null)
const loadError = ref(false)
const superfamilies = ref<any[]>([])
const sfCurrentPage = ref(1)
const sfPageSize = 20

const pagedSuperfamilies = computed(() => {
  const start = (sfCurrentPage.value - 1) * sfPageSize
  return superfamilies.value.slice(start, start + sfPageSize)
})

let chartInstance: echarts.ECharts | null = null
let rawData: any = null
let drillStack: any[] = []
let currentRoot: any = null

const isTopLevel = computed(() => !currentRoot || currentRoot.name === 'Transposable Element')

const centerLabel = computed(() => {
  if (!currentRoot) return 'TE Classification'
  const name = currentRoot.name
  if (name === 'Transposable Element') return 'TE Classification'
  return name.replace(/:\s*/, '\n')
})

const CLASS_I_COLORS = [
  '#e74c3c', '#e67e22', '#f39c12', '#d35400', '#c0392b',
  '#e55039', '#f6b93b', '#e58e26', '#fa983a', '#eb2f06',
  '#EE5A24', '#F79F1F', '#EA2027', '#FFC312', '#C4E538',
]
const CLASS_II_COLORS = [
  '#2980b9', '#27ae60', '#8e44ad', '#16a085', '#2c3e50',
  '#1abc9c', '#3498db', '#9b59b6', '#6C5CE7', '#0984e3',
  '#00b894', '#6c5ce7', '#00cec9', '#a29bfe', '#55efc4',
]

function calcNodeValue(node: any): number {
  if (!node.children || node.children.length === 0) {
    return Math.max(node.count || 0, 1)
  }
  return node.children.reduce((sum: number, c: any) => sum + calcNodeValue(c), 0)
}

function buildSunburstNode(child: any, idx: number, total: number, baseColor: string, depth: number = 0): any {
  const nodeColor = adjustColor(baseColor, idx, total)
  const node: any = {
    name: child.name,
    value: calcNodeValue(child),
    realCount: child.count || 0,
    itemStyle: {
      color: nodeColor,
      borderColor: '#fff',
      borderWidth: 2,
    },
  }

  if (child.children && child.children.length > 0 && depth < 4) {
    node.children = child.children.map((sub: any, subIdx: number) =>
      buildSunburstNode(sub, subIdx, child.children.length, nodeColor, depth + 1)
    )
  }

  return node
}

function getSunburstData(tree: any): any[] {
  if (!tree.children || tree.children.length === 0) {
    const isClassII = isInClassII(tree)
    const colorArr = isClassII ? CLASS_II_COLORS : CLASS_I_COLORS
    return [{
      name: tree.name,
      value: Math.max(tree.count || 0, 1),
      realCount: tree.count || 0,
      itemStyle: {
        color: colorArr[0],
        borderColor: '#fff',
        borderWidth: 2,
      },
    }]
  }

  return tree.children.map((child: any, idx: number) => {
    const isClassII = isInClassII(child)
    const colorArr = isClassII ? CLASS_II_COLORS : CLASS_I_COLORS
    const baseColor = colorArr[idx % colorArr.length]

    return buildSunburstNode(child, idx, tree.children.length, baseColor)
  })
}

function isInClassII(node: any): boolean {
  if (node.name.includes('Class II') || node.name.includes('DNA Transposon')) return true
  if (node.code && node.code.startsWith('D')) return true
  return false
}

function adjustColor(baseHex: string, index: number, total: number): string {
  const r = parseInt(baseHex.slice(1, 3), 16)
  const g = parseInt(baseHex.slice(3, 5), 16)
  const b = parseInt(baseHex.slice(5, 7), 16)

  const factor = 0.7 + (index / Math.max(total, 1)) * 0.6
  const nr = Math.min(255, Math.round(r * factor))
  const ng = Math.min(255, Math.round(g * factor))
  const nb = Math.min(255, Math.round(b * factor))

  return `#${nr.toString(16).padStart(2, '0')}${ng.toString(16).padStart(2, '0')}${nb.toString(16).padStart(2, '0')}`
}

function buildChartOption(data: any[]): any {
  return {
    tooltip: {
      formatter: (params: any) => {
        const d = params.data
        if (!d) return ''
        let html = `<strong>${d.name}</strong>`
        const info = findNodeInfo(rawData, d.name)
        if (info) {
          if (info.code) html += `<br/>Code: ${info.code}`
          if (info.aliases) html += `<br/>Aliases: ${info.aliases}`
          if (info.typical_tir) html += `<br/>TIR: ${info.typical_tir}`
          if (info.typical_tsd) html += `<br/>TSD: ${info.typical_tsd}`
          if (info.count > 0) html += `<br/><span style="color:#1a73e8">Entries: ${info.count}</span>`
          else html += `<br/><span style="color:#999">No entries yet</span>`
          if (info.children && info.children.length > 0) {
            html += `<br/><span style="color:#666">Click to drill down</span>`
          }
        }
        return html
      },
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#d0d7de',
      textStyle: { color: '#333', fontSize: 13 },
      padding: [10, 14],
    },
    series: [
      {
        type: 'sunburst',
        data: data,
        radius: ['15%', '95%'],
        nodeClick: false,
        sort: undefined,
        emphasis: {
          focus: 'ancestor',
        },
        label: {
          overflow: 'truncate',
        },
        itemStyle: {
          borderWidth: 1,
          borderColor: '#fff',
        },
        levels: [
          {},
          {
            r0: '15%',
            r: '40%',
            itemStyle: { borderWidth: 2, borderColor: '#fff' },
            label: {
              rotate: 'tangential',
              fontSize: 13,
              fontWeight: 'bold',
              color: '#fff',
              textShadowColor: 'rgba(0,0,0,0.4)',
              textShadowBlur: 4,
              overflow: 'truncate',
              width: 120,
              ellipsis: '...',
            },
          },
          {
            r0: '40%',
            r: '58%',
            itemStyle: { borderWidth: 1.5, borderColor: '#fff' },
            label: {
              rotate: 'tangential',
              fontSize: 11,
              fontWeight: 600,
              color: '#fff',
              textShadowColor: 'rgba(0,0,0,0.3)',
              textShadowBlur: 3,
              overflow: 'truncate',
              width: 100,
              ellipsis: '...',
            },
          },
          {
            r0: '58%',
            r: '74%',
            itemStyle: { borderWidth: 1, borderColor: '#fff' },
            label: {
              rotate: 'radial',
              fontSize: 10,
              color: '#fff',
              textShadowColor: 'rgba(0,0,0,0.3)',
              textShadowBlur: 2,
              overflow: 'truncate',
              width: 80,
              ellipsis: '...',
            },
          },
          {
            r0: '74%',
            r: '87%',
            itemStyle: { borderWidth: 0.5, borderColor: '#fff' },
            label: {
              rotate: 'radial',
              fontSize: 9,
              color: '#fff',
              textShadowColor: 'rgba(0,0,0,0.3)',
              textShadowBlur: 1,
              overflow: 'truncate',
              width: 60,
              ellipsis: '...',
            },
          },
          {
            r0: '87%',
            r: '95%',
            itemStyle: { borderWidth: 0.5, borderColor: '#fff' },
            label: {
              rotate: 'radial',
              fontSize: 9,
              color: '#fff',
              textShadowColor: 'rgba(0,0,0,0.2)',
              textShadowBlur: 1,
              overflow: 'truncate',
              width: 60,
              ellipsis: '...',
            },
          },
        ],
      },
    ],
  }
}

function findNodeInfo(node: any, name: string): any {
  if (!node) return null
  if (node.name === name) return node
  if (node.children) {
    for (const child of node.children) {
      const found = findNodeInfo(child, name)
      if (found) return found
    }
  }
  return null
}

onMounted(async () => {
  try {
    const resp = await fetch('/api/v1/classification/tree')
    const result = await resp.json()
    rawData = result.data || {}

    if (!rawData.children || rawData.children.length === 0) {
      loadError.value = true
      return
    }

    currentRoot = rawData
    drillStack = []

    await nextTick()
    initChart()

    fetch('/api/v1/classification/superfamilies')
      .then(r => r.json())
      .then(r => { superfamilies.value = r.data || [] })
      .catch(() => {})
  } catch (e) {
    console.error(e)
    loadError.value = true
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

function initChart() {
  if (!chartContainer.value) return

  chartInstance = echarts.init(chartContainer.value)
  renderChart()

  chartInstance.on('click', (params: any) => {
    if (!params.data) return
    const info = findNodeInfo(rawData, params.data.name)
    if (!info) return

    selectedInfo.value = { ...info }
    drillDown(info)
  })

  window.addEventListener('resize', handleResize)
}

function renderChart() {
  if (!chartInstance || !currentRoot) return
  const sunburstData = getSunburstData(currentRoot)
  const option = buildChartOption(sunburstData)
  chartInstance.setOption(option, true)
}

function onCenterClick() {
  if (drillStack.length > 0) {
    drillUp()
  }
}

function drillDown(node: any) {
  drillStack.push(currentRoot)
  currentRoot = node
  selectedInfo.value = null
  renderChart()
}

function drillUp() {
  if (drillStack.length === 0) return
  currentRoot = drillStack.pop()
  selectedInfo.value = null
  renderChart()
}

function handleResize() {
  chartInstance?.resize()
}

function onSearchInput() {
  if (!chartInstance || !rawData) return
  const text = searchKeyword.value.trim()

  if (!text) {
    resetView()
    return
  }

  const textRE = new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i')

  currentRoot = rawData
  drillStack = []

  const sunburstData = getSunburstData(rawData)
  highlightMatching(sunburstData, textRE)

  const option = buildChartOption(sunburstData)
  chartInstance.setOption(option, true)
}

function highlightMatching(nodes: any[], textRE: RegExp): void {
  for (const node of nodes) {
    const info = findNodeInfo(rawData, node.name)
    const isMatch = info && (
      textRE.test(info.name) ||
      (info.code && textRE.test(info.code)) ||
      (info.aliases && textRE.test(info.aliases))
    )

    if (isMatch) {
      node.itemStyle = {
        ...node.itemStyle,
        borderColor: '#FFD700',
        borderWidth: 3,
        shadowBlur: 12,
        shadowColor: 'rgba(255, 215, 0, 0.6)',
      }
    } else {
      node.itemStyle = {
        ...node.itemStyle,
        opacity: 0.35,
      }
    }

    if (node.children) {
      highlightMatching(node.children, textRE)
    }
  }
}

function resetView() {
  searchKeyword.value = ''
  selectedInfo.value = null
  currentRoot = rawData
  drillStack = []
  if (!chartInstance || !rawData) return

  renderChart()
}

function goToSearch(family: string) {
  router.push({ path: '/search', query: { family } })
}
</script>

<style scoped>
.classification-page { padding: 20px; }
.page-card { border-radius: 12px; }
.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 18px; font-weight: 600; color: #202124; }
.header-actions { display: flex; align-items: center; gap: 8px; }
.main-layout {
  display: flex;
  gap: 20px;
  min-height: 600px;
}
.chart-col {
  flex: 0 0 58%;
  max-width: 58%;
}
.sf-col {
  flex: 1;
  min-width: 0;
}
.sf-card-wrap {
  border-radius: 12px;
}
.sf-heading {
  font-size: 16px;
  font-weight: 600;
  color: #202124;
}
.sf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}
.sf-pagination {
  margin-top: 12px;
  display: flex;
  justify-content: center;
}
.sunburst-wrapper {
  position: relative;
  width: 100%;
  height: 680px;
}
.sunburst-container {
  width: 100%;
  height: 100%;
}
.center-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  z-index: 10;
}
.center-overlay.clickable {
  cursor: pointer;
}
.center-overlay.clickable:hover {
  box-shadow: 0 2px 12px rgba(26,115,232,0.2);
}
.center-text {
  text-align: center;
  font-weight: bold;
  font-size: 13px;
  color: #333;
  line-height: 1.4;
  white-space: pre-line;
  user-select: none;
}
.center-text.active {
  color: #1a73e8;
}
.error-msg {
  padding: 60px 0;
  text-align: center;
}
.detail-panel {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}
.sf-card {
  padding: 10px 12px;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
}
.sf-card:hover {
  border-color: #1a73e8;
  box-shadow: 0 1px 6px rgba(26,115,232,0.1);
}
.sf-name {
  font-weight: 600;
  font-size: 13px;
  color: #202124;
  margin-bottom: 4px;
}
.sf-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}
.sf-tag {
  font-size: 10px;
  color: #666;
  background: #f1f3f4;
  padding: 1px 5px;
  border-radius: 3px;
}
@media (max-width: 900px) {
  .main-layout {
    flex-direction: column;
  }
  .chart-col {
    flex: none;
    max-width: 100%;
  }
  .sunburst-wrapper {
    height: 500px;
  }
}
</style>
