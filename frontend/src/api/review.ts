import { get, post } from './request'
import type { ApiResponse } from '@/types/api'

export function getPendingReviews(params?: Record<string, any>): Promise<ApiResponse<{ items: any[]; total: number; page: number; page_size: number }>> {
  return get('/v1/review/pending', { params })
}

export function reviewTn(tnId: string, action: 'approve' | 'reject', comment?: string): Promise<ApiResponse<null>> {
  return post(`/v1/review/${tnId}`, { action, comment })
}

export function getReviewHistory(params?: Record<string, any>): Promise<ApiResponse<{ items: any[]; total: number; page: number; page_size: number }>> {
  return get('/v1/review/history', { params })
}
