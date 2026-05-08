import { get, post } from './request'
import type { ApiResponse } from '@/types/api'

export interface BlastParams {
  sequence: string
  program: 'blastn' | 'blastx' | 'tblastn' | 'blastp' | 'tblastx'
  evalue?: number
  max_target_seqs?: number
}

export interface BlastResult {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  hits?: BlastHit[]
}

export interface BlastHit {
  accession: string
  definition: string
  score: number
  evalue: number
  identity: number
  alignment_length: number
  query_start: number
  query_end: number
  subject_start: number
  subject_end: number
}

export function submitBlast(params: BlastParams): Promise<ApiResponse<{ task_id: string }>> {
  return post('/v1/blast', params)
}

export function getBlastStatus(taskId: string): Promise<ApiResponse<BlastResult>> {
  return get(`/v1/blast/${taskId}`)
}

export function getBlastResult(taskId: string): Promise<ApiResponse<BlastResult>> {
  return get(`/v1/blast/${taskId}/result`)
}
