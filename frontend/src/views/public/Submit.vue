<template>
  <div class="submit-page">
    <el-card shadow="never" class="page-card">
      <template #header>
        <span class="page-title">Submit Data</span>
      </template>

      <el-alert type="info" :closable="false" style="margin-bottom: 20px;">
        Fill in the core fields (marked with *), paste the DNA sequence, then click <strong>"Auto Analyze"</strong> to automatically detect TIR, ORF, and other features.
      </el-alert>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="160px">
        <el-divider content-position="left">Core Information (Required)</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Name" prop="name">
              <el-input v-model="form.name" placeholder="e.g. ISLEEU-1" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Family" prop="family">
              <el-select v-model="form.family" filterable allow-create style="width: 100%" placeholder="Select or type">
                <el-option v-for="f in families" :key="f" :label="f" :value="f" />
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
            <el-form-item label="Origin" prop="origin">
              <el-input v-model="form.origin" placeholder="Species name" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Accession No.">
              <el-input v-model="form.accession_number" placeholder="GCA_..." />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="MGE Type">
              <el-select v-model="form.mge_type" style="width: 100%" clearable>
                <el-option label="TE" value="TE" />
                <el-option label="MITE" value="MITE" />
                <el-option label="LARD" value="LARD" />
                <el-option label="TRIM" value="TRIM" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="DNA Sequence" prop="dna_sequence">
          <div style="width: 100%;">
            <el-input v-model="form.dna_sequence" type="textarea" :rows="6" placeholder="Paste DNA sequence (ATCG)..." style="font-family: monospace;" />
            <div style="margin-top: 8px; display: flex; gap: 10px; align-items: center;">
              <el-button type="success" @click="autoAnalyze" :loading="analyzing" :disabled="!form.dna_sequence || !form.family">
                <el-icon><MagicStick /></el-icon> Auto Analyze
              </el-button>
              <span v-if="!form.dna_sequence" class="hint-text">Paste sequence first</span>
              <span v-else-if="!form.family" class="hint-text">Select family for better analysis</span>
              <span v-else class="hint-text">Will detect TIR, ORF, TSD, and infer functions</span>
            </div>
          </div>
        </el-form-item>

        <el-divider content-position="left">
          Sequence Structure
          <el-tag size="small" type="info" effect="plain" round style="margin-left: 6px;">Auto-filled</el-tag>
        </el-divider>
        <el-row :gutter="20">
          <el-col :span="4">
            <el-form-item label="Length">
              <el-input-number v-model="form.length" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="IR">
              <el-input v-model="form.ir" placeholder="e.g. 12/13" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="DR">
              <el-input-number v-model="form.dr" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="ORF">
              <el-input v-model="form.orf" placeholder="e.g. 447/308" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="Transposition">
              <el-input v-model="form.transposition" placeholder="Cut-and-paste" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="Direct Repeat">
              <el-input v-model="form.direct_repeat" placeholder="TSD sequence" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="IRL (Left TIR)">
              <el-input v-model="form.irl" placeholder="Auto-detected" style="font-family: monospace;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="IRR (Right TIR)">
              <el-input v-model="form.irr" placeholder="Auto-detected" style="font-family: monospace;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Left Flank">
              <el-input v-model="form.left_flank" placeholder="Flanking sequence" style="font-family: monospace;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Right Flank">
              <el-input v-model="form.right_flank" placeholder="Flanking sequence" style="font-family: monospace;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">
          ORF1 Information
          <el-tag size="small" type="info" effect="plain" round style="margin-left: 6px;">Auto-filled</el-tag>
        </el-divider>
        <el-row :gutter="20">
          <el-col :span="4">
            <el-form-item label="ORF1 Begin">
              <el-input-number v-model="form.orf1_begin" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="ORF1 End">
              <el-input-number v-model="form.orf1_end" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="ORF1 Length">
              <el-input-number v-model="form.orf1_length" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="3">
            <el-form-item label="Strand">
              <el-select v-model="form.orf1_strand" style="width: 100%">
                <el-option label="+" value="+" />
                <el-option label="-" value="-" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="Function">
              <el-input v-model="form.orf1_function" placeholder="Transposase" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="Chemistry">
              <el-input v-model="form.orf1_chemistry" placeholder="DDE" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="ORF1 Name">
              <el-input v-model="form.orf1_name" placeholder="Optional" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Fusion ORF">
              <el-select v-model="form.orf1_fusion_orf" style="width: 100%">
                <el-option label="No" value="No" />
                <el-option label="Yes" value="Yes" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">
          ORF2 Information
          <el-tag size="small" type="info" effect="plain" round style="margin-left: 6px;">Auto-filled</el-tag>
        </el-divider>
        <el-row :gutter="20">
          <el-col :span="4">
            <el-form-item label="ORF2 Begin">
              <el-input-number v-model="form.orf2_begin" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="ORF2 End">
              <el-input-number v-model="form.orf2_end" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="ORF2 Length">
              <el-input-number v-model="form.orf2_length" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="3">
            <el-form-item label="Strand">
              <el-select v-model="form.orf2_strand" style="width: 100%">
                <el-option label="+" value="+" />
                <el-option label="-" value="-" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="Function">
              <el-input v-model="form.orf2_function" placeholder="Yqaj" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="Chemistry">
              <el-input v-model="form.orf2_chemistry" placeholder="DDE" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="ORF2 Name">
              <el-input v-model="form.orf2_name" placeholder="Optional" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Fusion ORF">
              <el-select v-model="form.orf2_fusion_orf" style="width: 100%">
                <el-option label="No" value="No" />
                <el-option label="Yes" value="Yes" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">Additional Information</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Synonyms">
              <el-input v-model="form.synonyms" placeholder="Alternative names" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Isoform">
              <el-input v-model="form.isoform" placeholder="Isoform identifier" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Related Elements">
              <el-input v-model="form.related_elements" placeholder="Related TEs" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitting">Submit</el-button>
          <el-button @click="resetForm">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import { createTn } from '@/api/tn'
import { analyzeSequence } from '@/api/analyze'

const submitting = ref(false)
const analyzing = ref(false)
const formRef = ref<FormInstance>()

const families = [
  'Tc1-Mariner', 'hAT', 'MuDR', 'EnSpm', 'piggyBac', 'P', 'Merlin',
  'PIF-Harbinger', 'Transib', 'Helitron', 'Crypton'
]

const form = reactive({
  name: '',
  family: '',
  tn_group: '',
  origin: '',
  mge_type: '' as string | undefined,
  accession_number: '',
  dna_sequence: '',
  length: undefined as number | undefined,
  ir: '',
  dr: undefined as number | undefined,
  orf: '',
  irl: '',
  irr: '',
  left_flank: '',
  right_flank: '',
  transposition: '',
  direct_repeat: '',
  synonyms: '',
  isoform: '',
  related_elements: '',
  orf1_name: '',
  orf1_length: undefined as number | undefined,
  orf1_begin: undefined as number | undefined,
  orf1_end: undefined as number | undefined,
  orf1_strand: '+' as string,
  orf1_fusion_orf: 'No',
  orf1_function: '',
  orf1_chemistry: '',
  orf2_name: '',
  orf2_length: undefined as number | undefined,
  orf2_begin: undefined as number | undefined,
  orf2_end: undefined as number | undefined,
  orf2_strand: '-' as string,
  orf2_fusion_orf: 'No',
  orf2_function: '',
  orf2_chemistry: '',
})

const rules: FormRules = {
  name: [{ required: true, message: 'Please enter a name', trigger: 'blur' }],
  family: [{ required: true, message: 'Please select a family', trigger: 'change' }],
  tn_group: [{ required: true, message: 'Please enter a group', trigger: 'blur' }],
  dna_sequence: [{ required: true, message: 'Please enter a sequence', trigger: 'blur' }],
  origin: [{ required: true, message: 'Please enter origin species', trigger: 'blur' }],
}

async function autoAnalyze() {
  if (!form.dna_sequence) {
    ElMessage.warning('Please paste DNA sequence first')
    return
  }
  analyzing.value = true
  try {
    const res = await analyzeSequence(form.dna_sequence, form.family || undefined)
    const r = res.data

    if (r.length) form.length = r.length
    if (r.ir) form.ir = r.ir
    if (r.dr != null) form.dr = r.dr
    if (r.irl) form.irl = r.irl
    if (r.irr) form.irr = r.irr
    if (r.orf) form.orf = r.orf
    if (r.direct_repeat) form.direct_repeat = r.direct_repeat
    if (r.mge_type) form.mge_type = r.mge_type
    if (r.transposition) form.transposition = r.transposition

    if (r.orf1_begin != null) form.orf1_begin = r.orf1_begin
    if (r.orf1_end != null) form.orf1_end = r.orf1_end
    if (r.orf1_length != null) form.orf1_length = r.orf1_length
    if (r.orf1_strand) form.orf1_strand = r.orf1_strand
    if (r.orf1_function) form.orf1_function = r.orf1_function
    if (r.orf1_chemistry) form.orf1_chemistry = r.orf1_chemistry

    if (r.orf2_begin != null) form.orf2_begin = r.orf2_begin
    if (r.orf2_end != null) form.orf2_end = r.orf2_end
    if (r.orf2_length != null) form.orf2_length = r.orf2_length
    if (r.orf2_strand) form.orf2_strand = r.orf2_strand
    if (r.orf2_function) form.orf2_function = r.orf2_function
    if (r.orf2_chemistry) form.orf2_chemistry = r.orf2_chemistry

    ElMessage.success('Analysis complete! Review and adjust the auto-filled fields.')
  } catch (e) {
    console.error(e)
    ElMessage.error('Analysis failed')
  } finally {
    analyzing.value = false
  }
}

async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate()

  submitting.value = true
  try {
    await createTn(form)
    ElMessage.success('Submitted successfully, pending review')
    resetForm()
  } catch (e) { console.error(e) }
  finally { submitting.value = false }
}

function resetForm() {
  formRef.value?.resetFields()
  Object.assign(form, {
    name: '', family: '', tn_group: '', origin: '', mge_type: undefined,
    accession_number: '', dna_sequence: '', length: undefined, ir: '',
    dr: undefined, orf: '', irl: '', irr: '', left_flank: '', right_flank: '',
    transposition: '', direct_repeat: '', synonyms: '', isoform: '', related_elements: '',
    orf1_name: '', orf1_length: undefined, orf1_begin: undefined, orf1_end: undefined,
    orf1_strand: '+', orf1_fusion_orf: 'No', orf1_function: '', orf1_chemistry: '',
    orf2_name: '', orf2_length: undefined, orf2_begin: undefined, orf2_end: undefined,
    orf2_strand: '-', orf2_fusion_orf: 'No', orf2_function: '', orf2_chemistry: '',
  })
}
</script>

<style scoped>
.submit-page { padding: 20px; }
.page-card { border-radius: 12px; }
.page-title { font-size: 18px; font-weight: 600; color: #202124; }
.hint-text { font-size: 12px; color: #909399; }

:deep(.el-divider__text) {
  font-weight: 600;
  color: #5f6368;
  font-size: 14px;
}
</style>
