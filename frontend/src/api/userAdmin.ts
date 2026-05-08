import { get, post, put, del } from './request'
import type { ApiResponse } from '@/types/api'
import type { User } from '@/types/user'

export function getUserList(params?: Record<string, any>): Promise<ApiResponse<{ items: User[]; total: number; page: number; page_size: number }>> {
  return get('/v1/admin/users', { params })
}

export function createUser(data: { username: string; email: string; password: string; role?: string; institution?: string }): Promise<ApiResponse<User>> {
  return post('/v1/admin/users', data)
}

export function updateUser(id: number, data: Record<string, any>): Promise<ApiResponse<User>> {
  return put(`/v1/admin/users/${id}`, data)
}

export function deleteUser(id: number): Promise<ApiResponse<null>> {
  return del(`/v1/admin/users/${id}`)
}
