import { get, post } from './request'
import type { ApiResponse } from '@/types/api'

export interface DownloadRequestData {
  requester_email: string
  requester_name?: string
  requester_institution?: string
  requested_data: string
  data_format: string
  purpose?: string
}

export interface AdminInfo {
  id: number
  username: string
  email: string
  institution: string | null
}

export function submitDownloadRequest(data: DownloadRequestData): Promise<ApiResponse<{ id: number; status: string }>> {
  return post('/v1/download-request', data)
}

export function getAdminList(): Promise<ApiResponse<AdminInfo[]>> {
  return get('/v1/download-request/admins')
}

export function getPendingDownloadRequests(params: { page: number; page_size: number }): Promise<ApiResponse<any>> {
  return get('/v1/download-request/pending', { params })
}

export function getDownloadRequestHistory(params: { page: number; page_size: number }): Promise<ApiResponse<any>> {
  return get('/v1/download-request/history', { params })
}

export function reviewDownloadRequest(requestId: number, action: 'approve' | 'reject', comment?: string): Promise<ApiResponse<any>> {
  return post(`/v1/download-request/${requestId}/review`, { action, comment })
}
