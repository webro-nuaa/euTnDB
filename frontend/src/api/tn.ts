import { get, post, put, del } from './request'
import type { TnEntry, TnFilter, TnListResponse } from '@/types/tn'
import type { ApiResponse } from '@/types/api'

export function getTnList(params: TnFilter): Promise<ApiResponse<TnListResponse>> {
  return get('/v1/tn', { params })
}

export function getTnDetail(id: string): Promise<ApiResponse<TnEntry>> {
  return get(`/v1/tn/${id}`)
}

export function createTn(data: Partial<TnEntry>): Promise<ApiResponse<TnEntry>> {
  return post('/v1/tn', data)
}

export function updateTn(id: string, data: Partial<TnEntry>): Promise<ApiResponse<TnEntry>> {
  return put(`/v1/tn/${id}`, data)
}

export function deleteTn(id: string): Promise<ApiResponse<null>> {
  return del(`/v1/tn/${id}`)
}

export function exportTn(format: 'fasta' | 'embl', ids: string[]): Promise<ApiResponse<{ url: string }>> {
  return post('/v1/export/batch', { format, ids })
}

export function importTn(file: File): Promise<ApiResponse<{ count: number }>> {
  const formData = new FormData()
  formData.append('file', file)
  return post('/v1/import/excel', formData)
}
