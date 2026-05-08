import { get, post } from './request'
import type { ApiResponse } from '@/types/api'

export interface MineTnParams {
  genome_file: string
  min_tir_length?: number
  max_tir_length?: number
  min_element_length?: number
  max_element_length?: number
  min_tir_similarity?: number
  threads?: number
}

export interface MineTnTask {
  id: number
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  genome_file: string
  parameters: Record<string, any>
  detected_count?: number
  result_file?: string
  error_message?: string
  created_at: string
  completed_at?: string
}

export interface MineTnResult {
  element_id: string
  chromosome: string
  start: number
  end: number
  strand: string
  length: number
  irl: string
  irr: string
  ir: string
  dr: number
  sequence: string
  family?: string
  mge_type?: string
}

export function createMineTnTask(params: MineTnParams): Promise<ApiResponse<{ taskId: string }>> {
  return post('/v1/minetn', params)
}

export function getMineTnTask(taskId: string): Promise<ApiResponse<MineTnTask>> {
  return get(`/v1/minetn/${taskId}`)
}

export function getMineTnResults(taskId: string): Promise<ApiResponse<MineTnResult[]>> {
  return get(`/v1/minetn/${taskId}/results`)
}

export function importMineTnResults(taskId: string, elementIds: string[]): Promise<ApiResponse<{ count: number }>> {
  return post(`/v1/minetn/${taskId}/import`, { element_ids: elementIds })
}

export function getMineTnTaskList(): Promise<ApiResponse<MineTnTask[]>> {
  return get('/v1/minetn')
}
