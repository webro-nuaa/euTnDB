import { get } from './request'
import type { ApiResponse } from '@/types/api'

export interface StatsOverview {
  tn_count: number
  species_count: number
  family_count: number
}

export interface FamilyStat {
  family: string
  count: number
}

export interface SpeciesStat {
  species: string
  count: number
}

export function getStatsOverview(): Promise<ApiResponse<StatsOverview>> {
  return get('/v1/stats/overview')
}

export function getFamilyStats(): Promise<ApiResponse<FamilyStat[]>> {
  return get('/v1/stats/family')
}

export function getSpeciesStats(): Promise<ApiResponse<SpeciesStat[]>> {
  return get('/v1/stats/species')
}
