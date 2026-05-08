import { get, put, post } from './request'
import type { ApiResponse } from '@/types/api'

export interface SystemSettings {
  site_name: string
  site_description: string
  default_status: string
  blast_enabled: string
  minetn_enabled: string
  max_upload_size: string
  smtp_host: string
  smtp_port: string
  smtp_user: string
  smtp_password: string
  smtp_from_name: string
  smtp_use_ssl: string
}

export function getSystemSettings(): Promise<ApiResponse<SystemSettings>> {
  return get('/v1/admin/settings')
}

export function updateSystemSettings(settings: Record<string, string>): Promise<ApiResponse<null>> {
  const settingsList = Object.entries(settings).map(([key, value]) => ({ key, value }))
  return put('/v1/admin/settings', { settings: settingsList })
}

export function testEmail(testEmail: string): Promise<ApiResponse<null>> {
  return post('/v1/admin/settings/test-email', { test_email: testEmail })
}
