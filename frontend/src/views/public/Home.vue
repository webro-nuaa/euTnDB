<template>
  <div class="home-page">
    <div class="hero">
      <div class="hero-content">
        <h1>euTnDB</h1>
        <h2>Tn in Eukaryotes</h2>
        <p class="subtitle">A comprehensive database of DNA transposons with Terminal Inverted Repeats (TIR) in eukaryotic genomes</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round @click="$router.push('/classification')">Browse Data</el-button>
          <el-button size="large" round @click="$router.push('/blast')">BLAST Search</el-button>
        </div>
      </div>
    </div>

    <div class="features">
      <el-row :gutter="24">
        <el-col :span="6">
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon :size="32"><Collection /></el-icon>
            </div>
            <h4>Comprehensive Collection</h4>
            <p>Covers multiple superfamilies of DNA transposons across diverse species</p>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon :size="32"><Search /></el-icon>
            </div>
            <h4>BLAST Search</h4>
            <p>Sequence similarity search powered by BLAST for efficient transposon identification</p>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon :size="32"><Download /></el-icon>
            </div>
            <h4>Data Export</h4>
            <p>Export in FASTA and EMBL (RepBase-compatible) formats for downstream analysis</p>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="feature-card">
            <div class="feature-icon">
              <el-icon :size="32"><Cpu /></el-icon>
            </div>
            <h4>MineTn Integration</h4>
            <p>De novo transposon detection from genome sequences via MineTn pipeline</p>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-row :gutter="24" class="content-row">
      <el-col :span="14">
        <el-card shadow="never" class="content-card">
          <h3>About euTnDB</h3>
          <p>
            Tn in Eukaryotes (euTnDB) is a curated database dedicated to the collection and annotation of DNA transposons
            characterized by Terminal Inverted Repeats (TIRs) in eukaryotic genomes. These Class II transposable elements
            mobilize via a "cut-and-paste" mechanism and are widespread across eukaryotic genomes.
          </p>
          <p>
            TIRs are inverted repeat sequences at both ends of a DNA transposon that serve as
            recognition sites for transposases. Their length and sequence features vary among
            superfamilies, making them essential for transposon classification and identification.
          </p>
          <p>
            All data in euTnDB are sourced from published literature and public databases, and have
            been manually curated to ensure accuracy and reliability. Researchers are welcome to
            submit new transposon entries for inclusion.
          </p>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never" class="content-card">
          <h3>Key Features</h3>
          <ul class="feature-list">
            <li>Multiple superfamilies: Tc1-Mariner, hAT, MuDR, EnSpm, piggyBac, and more</li>
            <li>Complete TIR sequence information</li>
            <li>BLAST-based sequence similarity search</li>
            <li>RepBase-compatible EMBL format export</li>
            <li>FASTA format data download</li>
            <li>MineTn integration for de novo detection</li>
            <li>Community data submission</li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { Collection, Search, Download, Cpu } from '@element-plus/icons-vue'
</script>

<style scoped>
.home-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px 40px;
}

.hero {
  background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 50%, #1565c0 100%);
  color: #fff;
  border-radius: 0 0 16px 16px;
  margin: 0 -20px 40px;
  padding: 0 20px;
}

.hero-content {
  max-width: 1100px;
  margin: 0 auto;
  text-align: center;
  padding: 80px 20px 60px;
}

.hero h1 {
  font-size: 56px;
  margin-bottom: 8px;
  letter-spacing: 3px;
  font-weight: 800;
}

.hero h2 {
  font-size: 22px;
  font-weight: 400;
  margin-bottom: 16px;
  opacity: 0.95;
}

.hero .subtitle {
  font-size: 16px;
  opacity: 0.85;
  margin-bottom: 32px;
  max-width: 560px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.hero-actions .el-button {
  min-width: 150px;
}

.features {
  margin-bottom: 40px;
}

.feature-card {
  background: #fff;
  border-radius: 12px;
  padding: 28px 20px;
  text-align: center;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #e8f0fe;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #1a73e8;
}

.feature-card h4 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #202124;
}

.feature-card p {
  margin: 0;
  font-size: 13px;
  color: #5f6368;
  line-height: 1.6;
}

.content-row {
  margin-bottom: 20px;
}

.content-card {
  border-radius: 12px;
}

.content-card h3 {
  font-size: 18px;
  color: #202124;
  margin: 0 0 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #1a73e8;
}

.content-card p {
  font-size: 14px;
  color: #5f6368;
  line-height: 1.8;
  margin-bottom: 12px;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  font-size: 14px;
  color: #5f6368;
  line-height: 2;
  padding-left: 20px;
  position: relative;
}

.feature-list li::before {
  content: "✓";
  color: #1a73e8;
  font-weight: bold;
  position: absolute;
  left: 0;
}
</style>
