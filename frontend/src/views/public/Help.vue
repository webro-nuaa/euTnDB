<template>
  <div class="help-page">
    <el-card shadow="never" class="page-card">
      <template #header>
        <span class="page-title">Help</span>
      </template>

      <el-collapse v-model="activeNames">
        <el-collapse-item title="How to search Tn data?" name="1">
          <p>You can search Tn data in the following ways:</p>
          <ol>
            <li>Use the <strong>Search</strong> page to filter by keyword, superfamily, species, type, etc.</li>
            <li>Use the <strong>Classification</strong> page to browse by major class and superfamily</li>
            <li>Use the <strong>BLAST</strong> page to find similar transposons by sequence alignment</li>
          </ol>
        </el-collapse-item>

        <el-collapse-item title="How to submit data?" name="2">
          <p>Click the <strong>Submit Data</strong> button in the navigation bar, fill in the transposon information, and submit. Submitted data will enter the review queue and become publicly visible after admin approval.</p>
        </el-collapse-item>

        <el-collapse-item title="How to download data?" name="3">
          <p>You can download data in the following ways:</p>
          <ol>
            <li>On the <strong>Download</strong> page, select a format (FASTA/EMBL) and filter conditions for batch download</li>
            <li>On the Tn detail page, click "Download FASTA" or "Download EMBL" for individual entries</li>
            <li>On the search results page, click "Export Results" to download search results</li>
          </ol>
        </el-collapse-item>

        <el-collapse-item title="How to use BLAST?" name="4">
          <p>On the BLAST page:</p>
          <ol>
            <li>Select a BLAST program (blastn/blastx/tblastn)</li>
            <li>Enter the query sequence</li>
            <li>Set the E-value threshold and maximum number of target sequences</li>
            <li>Click "Run BLAST" and wait for results</li>
          </ol>
        </el-collapse-item>

        <el-collapse-item title="What is the EMBL format?" name="5">
          <p>The EMBL format is the standard format used by the RepBase database, containing complete annotation information for transposons. EMBL files exported from euTnDB are compatible with RepBase and can be directly used in other bioinformatics tools.</p>
        </el-collapse-item>

        <el-collapse-item title="How to contact us?" name="6">
          <p>For questions or suggestions, please contact us at:</p>
          <ul>
            <li>Email: tndb@example.com</li>
          </ul>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeNames = ref(['1'])
</script>

<style scoped>
.help-page { padding: 20px; }
.page-card { border-radius: 12px; }
.page-title { font-size: 18px; font-weight: 600; color: #202124; }
p { color: #5f6368; line-height: 1.8; }
ol, ul { padding-left: 20px; }
li { color: #5f6368; line-height: 2; }
</style>
