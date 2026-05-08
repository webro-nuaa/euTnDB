import { post } from './request'
import type { ApiResponse } from '@/types/api'

export interface AnalyzeResult {
  length: number
  gc_content: number
  irl: string | null
  irr: string | null
  ir: string | null
  dr: number | null
  direct_repeat: string | null
  orf1_begin: number | null
  orf1_end: number | null
  orf1_length: number | null
  orf1_strand: string | null
  orf2_begin: number | null
  orf2_end: number | null
  orf2_length: number | null
  orf2_strand: string | null
  orf: string | null
  orf1_function: string | null
  orf1_chemistry: string | null
  orf2_function: string | null
  orf2_chemistry: string | null
  transposition: string | null
  mge_type: string | null
}

export function analyzeSequence(dnaSequence: string, family?: string): Promise<ApiResponse<AnalyzeResult>> {
  return post('/v1/analyze/sequence', { dna_sequence: dnaSequence, family })
}
