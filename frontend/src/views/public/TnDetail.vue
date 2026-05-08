<template>
  <div class="tn-detail-page">
    <el-card v-loading="loading" shadow="never" class="page-card">
      <template #header>
        <div class="card-header">
          <div>
            <h2>{{ tn.name }}</h2>
            <p class="subtitle">{{ tn.family }} transposon from the {{ tn.origin || 'unknown' }} genome</p>
          </div>
          <div class="actions">
            <el-button type="primary" @click="downloadFasta">Download FASTA</el-button>
            <el-button @click="downloadEmbl">Download EMBL</el-button>
          </div>
        </div>
      </template>

      <div class="embl-view">
        <div class="embl-section">
          <div class="embl-line"><span class="embl-tag">ID</span>  {{ tn.name }} DNA; {{ tn.mge_type || 'TE' }}; {{ tn.length || '?' }} BP.</div>
          <div class="embl-line"><span class="embl-tag">XX</span></div>

          <div class="embl-line"><span class="embl-tag">DE</span>  {{ tn.family }} transposon from the {{ tn.origin || 'unknown' }} genome{{ tn.isoform ? `, isoform ${tn.isoform}` : '' }}.</div>
          <div class="embl-line"><span class="embl-tag">XX</span></div>

          <div class="embl-line"><span class="embl-tag">AC</span>  {{ tn.accession_number || '.' }}</div>
          <div class="embl-line"><span class="embl-tag">XX</span></div>

          <div class="embl-line"><span class="embl-tag">DT</span>  {{ formatDate(tn.created_at) }} (Created)</div>
          <div class="embl-line"><span class="embl-tag">DT</span>  {{ formatDate(tn.updated_at) }} (Last updated)</div>
          <div class="embl-line"><span class="embl-tag">XX</span></div>

          <div class="embl-line">
            <span class="embl-tag">KW</span>  {{ tn.name }}; {{ tn.family }}; {{ tn.tn_group }}; {{ tn.mge_type || 'TE' }};{{ tn.synonyms ? ` ${tn.synonyms};` : '' }}
          </div>
          <div class="embl-line"><span class="embl-tag">XX</span></div>

          <div class="embl-line"><span class="embl-tag">OS</span>  {{ tn.origin || '.' }}</div>
          <div class="embl-line"><span class="embl-tag">OC</span>  {{ tn.origin || '.' }}</div>
          <div class="embl-line"><span class="embl-tag">XX</span></div>

          <div class="embl-line">
            <span class="embl-tag">CC</span>
            <span class="embl-cc">
              IR: {{ tn.ir || '-' }}; DR: {{ tn.dr ?? '-' }}; ORF: {{ tn.orf || '-' }};
              Transposition: {{ tn.transposition || '-' }}; Direct repeat: {{ tn.direct_repeat || '-' }}.
            </span>
          </div>
          <div class="embl-line"><span class="embl-tag">XX</span></div>

          <template v-if="tn.related_elements">
            <div class="embl-line"><span class="embl-tag">DR</span>  Related element(s): {{ tn.related_elements }}</div>
            <div class="embl-line"><span class="embl-tag">XX</span></div>
          </template>
        </div>

        <el-divider>ORF1 Information</el-divider>
        <div class="embl-section">
          <div class="embl-line"><span class="embl-tag">FH</span>  ORF1: {{ tn.orf1_function || '.' }} ({{ tn.orf1_chemistry || '.' }})</div>
          <div class="embl-line"><span class="embl-tag">FT</span>  source          {{ tn.orf1_begin || '?' }}..{{ tn.orf1_end || '?' }}</div>
          <div class="embl-line"><span class="embl-tag">FT</span>                  /strand="{{ tn.orf1_strand || '+' }}"</div>
          <div class="embl-line"><span class="embl-tag">FT</span>                  /length="{{ tn.orf1_length || '?' }}"</div>
          <div class="embl-line"><span class="embl-tag">FT</span>                  /function="{{ tn.orf1_function || '.' }}"</div>
          <div class="embl-line"><span class="embl-tag">FT</span>                  /chemistry="{{ tn.orf1_chemistry || '.' }}"</div>
          <div class="embl-line"><span class="embl-tag">FT</span>                  /fusion_ORF="{{ tn.orf1_fusion_orf || 'No' }}"</div>
          <div v-if="tn.orf1_sequence" class="embl-line">
            <span class="embl-tag">FT</span>                  /protein_sequence="{{ truncateSeq(tn.orf1_sequence) }}"
          </div>
        </div>

        <el-divider>ORF2 Information</el-divider>
        <div class="embl-section">
          <div class="embl-line"><span class="embl-tag">FH</span>  ORF2: {{ tn.orf2_function || '.' }} ({{ tn.orf2_chemistry || '.' }})</div>
          <div class="embl-line"><span class="embl-tag">FT</span>  source          {{ tn.orf2_begin || '?' }}..{{ tn.orf2_end || '?' }}</div>
          <div class="embl-line"><span class="embl-tag">FT</span>                  /strand="{{ tn.orf2_strand || '+' }}"</div>
          <div class="embl-line"><span class="embl-tag">FT</span>                  /length="{{ tn.orf2_length || '?' }}"</div>
          <div class="embl-line"><span class="embl-tag">FT</span>                  /function="{{ tn.orf2_function || '.' }}"</div>
          <div class="embl-line"><span class="embl-tag">FT</span>                  /chemistry="{{ tn.orf2_chemistry || '.' }}"</div>
          <div class="embl-line"><span class="embl-tag">FT</span>                  /fusion_ORF="{{ tn.orf2_fusion_orf || 'No' }}"</div>
          <div v-if="tn.orf2_sequence" class="embl-line">
            <span class="embl-tag">FT</span>                  /protein_sequence="{{ truncateSeq(tn.orf2_sequence) }}"
          </div>
        </div>

        <el-divider>TIR / Flanking Sequences</el-divider>
        <div class="embl-section">
          <div v-if="tn.irl" class="embl-line"><span class="embl-tag">FT</span>  IRL             "{{ tn.irl }}"</div>
          <div v-if="tn.irr" class="embl-line"><span class="embl-tag">FT</span>  IRR             "{{ tn.irr }}"</div>
          <div v-if="tn.left_flank" class="embl-line"><span class="embl-tag">FT</span>  left_flank      "{{ truncateSeq(tn.left_flank) }}"</div>
          <div v-if="tn.right_flank" class="embl-line"><span class="embl-tag">FT</span>  right_flank     "{{ truncateSeq(tn.right_flank) }}"</div>
          <div v-if="!tn.irl && !tn.irr && !tn.left_flank && !tn.right_flank" class="embl-line">
            <span class="embl-tag">CC</span>  No TIR/flanking sequence data available.
          </div>
        </div>

        <el-divider>DNA Sequence</el-divider>
        <div class="embl-section">
          <div class="embl-line"><span class="embl-tag">SQ</span>  Sequence {{ tn.length || 0 }} BP;</div>
          <div v-if="tn.dna_sequence" class="sequence-block">
            <div class="seq-name">{{ tn.name }}</div>
            <div class="seq-content">{{ formatSequence(tn.dna_sequence) }}</div>
          </div>
          <div v-else class="embl-line"><span class="embl-tag">CC</span>  No DNA sequence available.</div>
        </div>
      </div>

      <el-divider>Structured Data</el-divider>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="Name">{{ tn.name }}</el-descriptions-item>
        <el-descriptions-item label="Family">{{ tn.family }}</el-descriptions-item>
        <el-descriptions-item label="Group">{{ tn.tn_group }}</el-descriptions-item>
        <el-descriptions-item label="Synonyms">{{ tn.synonyms || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Isoform">{{ tn.isoform || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Accession">{{ tn.accession_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Origin">{{ tn.origin || '-' }}</el-descriptions-item>
        <el-descriptions-item label="MGE Type">{{ tn.mge_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Related Elements">{{ tn.related_elements || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Length">{{ tn.length ? tn.length + ' bp' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="IR">{{ tn.ir || '-' }}</el-descriptions-item>
        <el-descriptions-item label="DR">{{ tn.dr ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF">{{ tn.orf || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Transposition">{{ tn.transposition || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Direct Repeat">{{ tn.direct_repeat || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider>ORF1 Details</el-divider>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="ORF1 Name">{{ tn.orf1_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF1 Length">{{ tn.orf1_length ? tn.orf1_length + ' bp' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF1 Position">{{ tn.orf1_begin && tn.orf1_end ? `${tn.orf1_begin}..${tn.orf1_end}` : '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF1 Strand">{{ tn.orf1_strand || '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF1 Fusion">{{ tn.orf1_fusion_orf || '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF1 Function">{{ tn.orf1_function || '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF1 Chemistry">{{ tn.orf1_chemistry || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider>ORF2 Details</el-divider>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="ORF2 Name">{{ tn.orf2_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF2 Length">{{ tn.orf2_length ? tn.orf2_length + ' bp' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF2 Position">{{ tn.orf2_begin && tn.orf2_end ? `${tn.orf2_begin}..${tn.orf2_end}` : '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF2 Strand">{{ tn.orf2_strand || '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF2 Fusion">{{ tn.orf2_fusion_orf || '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF2 Function">{{ tn.orf2_function || '-' }}</el-descriptions-item>
        <el-descriptions-item label="ORF2 Chemistry">{{ tn.orf2_chemistry || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getTnDetail } from '@/api/tn'
import type { TnEntry } from '@/types/tn'

const route = useRoute()
const loading = ref(false)
const tn = ref<Partial<TnEntry>>({
  name: '',
  family: '',
  tn_group: '',
})

onMounted(() => {
  loadTnDetail()
})

async function loadTnDetail() {
  const id = route.params.id as string
  loading.value = true
  try {
    const res = await getTnDetail(id)
    tn.value = res.data
  } catch (e) {
    ElMessage.error('Failed to load Tn detail')
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '.'
  const d = new Date(dateStr)
  const day = String(d.getDate()).padStart(2, '0')
  const months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
  const month = months[d.getMonth()]
  const year = d.getFullYear()
  return `${day}-${month}-${year}`
}

function truncateSeq(seq: string, maxLen: number = 60): string {
  if (!seq) return ''
  if (seq.length <= maxLen) return seq
  return seq.substring(0, maxLen) + '...'
}

function formatSequence(seq: string): string {
  if (!seq) return ''
  const lines = []
  for (let i = 0; i < seq.length; i += 60) {
    lines.push(seq.substring(i, i + 60))
  }
  return lines.join('\n')
}

function downloadFasta() {
  const id = route.params.id as string
  window.open(`/api/v1/export/fasta/${id}`, '_blank')
}

function downloadEmbl() {
  const id = route.params.id as string
  window.open(`/api/v1/export/embl/${id}`, '_blank')
}
</script>

<style scoped>
.tn-detail-page { padding: 20px; }
.page-card { border-radius: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; }
.card-header h2 { margin: 0; font-size: 20px; color: #202124; }
.subtitle { color: #909399; margin: 5px 0 0; font-size: 14px; }
.actions { display: flex; gap: 10px; }

.embl-view {
  background: #fafbfc;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  padding: 20px 24px;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: #3c4043;
  overflow-x: auto;
}

.embl-section {
  margin-bottom: 4px;
}

.embl-line {
  white-space: pre-wrap;
  word-break: break-all;
}

.embl-tag {
  display: inline-block;
  width: 24px;
  color: #1a73e8;
  font-weight: 600;
  margin-right: 8px;
  text-align: right;
}

.embl-cc {
  color: #5f6368;
}

.sequence-block {
  margin-top: 8px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid #e8eaed;
  border-radius: 6px;
}

.seq-name {
  font-weight: 600;
  color: #1a73e8;
  margin-bottom: 8px;
}

.seq-content {
  white-space: pre-wrap;
  word-break: break-all;
  color: #202124;
  letter-spacing: 0.5px;
}

:deep(.el-divider__text) {
  font-weight: 600;
  color: #5f6368;
  font-size: 14px;
}
</style>
