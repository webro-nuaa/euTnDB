import { get } from './request'
import type { TnFilter, TnListResponse } from '@/types/tn'
import type { ApiResponse } from '@/types/api'

export interface SearchSuggestion {
  type: 'name' | 'family' | 'tn_group' | 'origin'
  value: string
  label: string
}

export function searchTn(params: TnFilter): Promise<ApiResponse<TnListResponse>> {
  return get('/v1/search', { params })
}

export function getSearchSuggestions(keyword: string): Promise<ApiResponse<SearchSuggestion[]>> {
  return get('/v1/search/suggestions', { params: { keyword } })
}
