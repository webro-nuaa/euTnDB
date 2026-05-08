<template>
  <div class="blast-page">
    <el-card shadow="never" class="page-card">
      <template #header>
        <span class="page-title">BLAST Sequence Search</span>
      </template>

      <el-form :model="form" label-width="140px">
        <el-form-item label="Program">
          <el-radio-group v-model="form.program">
            <el-radio-button value="blastn">blastn</el-radio-button>
            <el-radio-button value="blastp">blastp</el-radio-button>
            <el-radio-button value="blastx">blastx</el-radio-button>
            <el-radio-button value="tblastn">tblastn</el-radio-button>
            <el-radio-button value="tblastx">tblastx</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Query Sequence">
          <el-input
            v-model="form.sequence"
            type="textarea"
            :rows="6"
            :placeholder="sequencePlaceholder"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="E-value Threshold">
              <el-select v-model="form.evalue" style="width: 100%">
                <el-option label="1e-50" :value="1e-50" />
                <el-option label="1e-20" :value="1e-20" />
                <el-option label="1e-10" :value="1e-10" />
                <el-option label="1e-5" :value="1e-5" />
                <el-option label="1e-3" :value="1e-3" />
                <el-option label="1" :value="1" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Max Target Seqs">
              <el-input-number v-model="form.max_target_seqs" :min="1" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="submitBlast" :loading="submitting" :disabled="!form.sequence">
            Run BLAST
          </el-button>
          <el-button @click="form.sequence = ''">Clear</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="taskId" shadow="never" class="page-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>BLAST Results</span>
          <el-tag :type="getStatusType(taskStatus)">{{ taskStatus }}</el-tag>
        </div>
      </template>

      <div v-if="taskStatus === 'running'" style="text-align: center; padding: 40px;">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <p>Running BLAST search, please wait...</p>
      </div>

      <div v-else-if="taskStatus === 'completed' && hits.length > 0">
        <el-table :data="hits" style="width: 100%">
          <el-table-column prop="name" label="Name" width="140">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/tn/${row.name}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="family" label="Family" width="140" />
          <el-table-column prop="origin" label="Origin" show-overflow-tooltip />
          <el-table-column prop="identity" label="Identity" width="100">
            <template #default="{ row }">{{ (row.identity * 100).toFixed(1) }}%</template>
          </el-table-column>
          <el-table-column prop="evalue" label="E-value" width="100">
            <template #default="{ row }">{{ row.evalue.toExponential(2) }}</template>
          </el-table-column>
          <el-table-column prop="score" label="Score" width="80" />
          <el-table-column prop="alignment_length" label="Alignment" width="100" />
        </el-table>
      </div>

      <el-empty v-else-if="taskStatus === 'completed' && hits.length === 0" description="No significant hits found" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { submitBlast as submitBlastApi, getBlastStatus } from '@/api/blast'

const submitting = ref(false)
const taskId = ref('')
const taskStatus = ref('')
const hits = ref<any[]>([])

const form = reactive({
  sequence: '',
  program: 'blastn',
  evalue: 1e-5,
  max_target_seqs: 10
})

const PROTEIN_PROGRAMS = new Set(['blastp', 'tblastx'])

const sequencePlaceholder = computed(() => {
  if (PROTEIN_PROGRAMS.has(form.program)) {
    return 'Enter a protein sequence in FASTA format (e.g., MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHF...)'
  }
  return 'Enter a nucleotide sequence in FASTA format (e.g., ATCGATCGATCG...)'
})

async function submitBlast() {
  if (!form.sequence.trim()) {
    ElMessage.warning('Please enter a sequence')
    return
  }

  submitting.value = true
  hits.value = []
  taskStatus.value = 'pending'

  try {
    const res = await submitBlastApi({
      sequence: form.sequence,
      program: form.program as any,
      evalue: form.evalue,
      max_target_seqs: form.max_target_seqs
    })
    taskId.value = res.data.task_id
    pollResult()
  } catch (e) {
    console.error(e)
    ElMessage.error('Failed to submit BLAST search')
  } finally {
    submitting.value = false
  }
}

async function pollResult() {
  const poll = async () => {
    try {
      const res = await getBlastStatus(taskId.value)
      taskStatus.value = res.data.status

      if (res.data.status === 'completed') {
        hits.value = res.data.hits || []
        return
      } else if (res.data.status === 'failed') {
        ElMessage.error('BLAST search failed')
        return
      }

      setTimeout(poll, 2000)
    } catch (e) { console.error(e) }
  }

  setTimeout(poll, 1000)
}

function getStatusType(status: string) {
  const types: Record<string, string> = { pending: 'info', running: 'warning', completed: 'success', failed: 'danger' }
  return types[status] || 'info'
}
</script>

<style scoped>
.blast-page { padding: 20px; }
.page-card { border-radius: 12px; }
.page-title { font-size: 18px; font-weight: 600; color: #202124; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
