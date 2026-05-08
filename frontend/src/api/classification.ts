import { get } from './request'
import type { ApiResponse } from '@/types/api'

export function getClassificationTree(): Promise<ApiResponse<any>> {
  return get('/v1/classification/tree')
}

export function getSuperfamilies(): Promise<ApiResponse<any[]>> {
  return get('/v1/classification/superfamilies')
}
