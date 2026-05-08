<template>
  <div class="knowledge-page">
    <el-card shadow="never" class="page-card">
      <template #header>
        <span class="page-title">Knowledge Base</span>
      </template>

      <el-collapse v-model="activeNames">
        <el-collapse-item title="What are DNA transposons?" name="1">
          <p>DNA transposons are a class of transposable elements that mobilize via a "cut-and-paste" mechanism. They belong to Class II transposable elements and are characterized by Terminal Inverted Repeats (TIRs) at both ends.</p>
          <p>DNA transposons are widespread in eukaryotic genomes and play important roles in genome structural variation and gene expression regulation.</p>
        </el-collapse-item>

        <el-collapse-item title="What are TIRs?" name="2">
          <p>Terminal Inverted Repeats (TIRs) are inverted repeat sequences found at both ends of a DNA transposon. The left TIR and right TIR are reverse complements of each other and serve as key recognition and binding sites for transposases.</p>
          <p>TIR length and sequence features vary among superfamilies, making them essential for DNA transposon classification. For example:</p>
          <ul>
            <li>Tc1-Mariner superfamily: TIR length typically 28-40 bp</li>
            <li>hAT superfamily: TIR length typically 5-27 bp</li>
            <li>MuDR superfamily: TIR length typically 100-300 bp</li>
          </ul>
        </el-collapse-item>

        <el-collapse-item title="What are TSDs?" name="3">
          <p>Target Site Duplications (TSDs) are short duplicated sequences generated at both ends of a DNA transposon upon insertion into the genome. TSD length and sequence features vary among superfamilies and serve as auxiliary criteria for classification.</p>
          <p>Common TSD features by superfamily:</p>
          <ul>
            <li>Tc1-Mariner: TA</li>
            <li>hAT: 8 bp</li>
            <li>MuDR: 9 bp</li>
            <li>EnSpm: 3 bp</li>
          </ul>
        </el-collapse-item>

        <el-collapse-item title="Autonomous vs. Non-autonomous Transposons" name="4">
          <p><strong>Autonomous transposons</strong> encode a functional transposase and can mobilize independently.</p>
          <p><strong>Non-autonomous transposons</strong> lack a functional transposase and require the transposase encoded by an autonomous element from the same superfamily to mobilize.</p>
          <p>Non-autonomous elements typically retain their TIR sequences but have internal deletions or mutations in the coding region.</p>
        </el-collapse-item>

        <el-collapse-item title="DNA Transposon Superfamily Classification" name="5">
          <p>DNA transposons are classified into superfamilies based on TIR features, TSD features, and transposase domain structure:</p>
          <el-table :data="superfamilies" style="width: 100%" size="small">
            <el-table-column prop="name" label="Superfamily" width="150" />
            <el-table-column prop="tir" label="TIR Length" width="120" />
            <el-table-column prop="tsd" label="TSD" width="100" />
            <el-table-column prop="domain" label="Transposase Domain" />
          </el-table>
        </el-collapse-item>

        <el-collapse-item title="RepBase Format" name="6">
          <p>RepBase is the standard format for repetitive DNA element databases. euTnDB supports RepBase-compatible EMBL format export, which includes:</p>
          <ul>
            <li>ID line: Accession and basic sequence information</li>
            <li>AC line: Accession number</li>
            <li>DE line: Description</li>
            <li>OS/OC lines: Organism and classification</li>
            <li>FT lines: Feature annotations (TIR, TSD, ORF, etc.)</li>
            <li>SQ line: Sequence data</li>
          </ul>
        </el-collapse-item>

        <el-collapse-item title="MineTn Tool" name="7">
          <p>MineTn is a bioinformatics tool for de novo detection of DNA transposons from genome sequences. It identifies potential DNA transposon elements by detecting TIR sequences.</p>
          <p>Key features:</p>
          <ul>
            <li>TIR-based transposon identification</li>
            <li>Customizable TIR length and similarity thresholds</li>
            <li>Automatic superfamily classification</li>
            <li>Results can be directly imported into euTnDB</li>
          </ul>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeNames = ref(['1'])

const superfamilies = [
  { name: 'Tc1-Mariner', tir: '28-40 bp', tsd: 'TA', domain: 'DDE' },
  { name: 'hAT', tir: '5-27 bp', tsd: '8 bp', domain: 'DDE-T' },
  { name: 'MuDR', tir: '100-300 bp', tsd: '9 bp', domain: 'DDE' },
  { name: 'EnSpm', tir: '12-18 bp', tsd: '3 bp', domain: 'DDE' },
  { name: 'piggyBac', tir: '13-16 bp', tsd: 'TTAA', domain: 'DDE' },
  { name: 'P', tir: '~46 bp', tsd: '8 bp', domain: 'THAP' },
  { name: 'Merlin', tir: '14-20 bp', tsd: 'TTAA', domain: 'DDE' },
  { name: 'Harbinger', tir: '14-24 bp', tsd: '3 bp', domain: 'DDE' },
  { name: 'Transib', tir: '~30 bp', tsd: '5 bp', domain: 'DDE' },
  { name: 'Crypton', tir: 'variable', tsd: 'variable', domain: 'Y1/Y2' },
]
</script>

<style scoped>
.knowledge-page { padding: 20px; }
.page-card { border-radius: 12px; }
.page-title { font-size: 18px; font-weight: 600; color: #202124; }
p { color: #5f6368; line-height: 1.8; }
ul { padding-left: 20px; }
li { color: #5f6368; line-height: 2; }
</style>
