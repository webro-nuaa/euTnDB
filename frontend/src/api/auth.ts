import { get, post } from './request'
import type { User } from '@/types/user'
import type { ApiResponse } from '@/types/api'

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  email: string
  password: string
  institution?: string
}

export interface LoginResponse {
  token: string
  user: User
}

export function login(params: LoginParams): Promise<ApiResponse<LoginResponse>> {
  return post('/v1/auth/login', params)
}

export function register(params: RegisterParams): Promise<ApiResponse<User>> {
  return post('/v1/auth/register', params)
}

export function logout(): Promise<ApiResponse<null>> {
  return post('/v1/auth/logout')
}

export function getCurrentUser(): Promise<ApiResponse<User>> {
  return get('/v1/auth/me')
}

export function changePassword(oldPassword: string, newPassword: string): Promise<ApiResponse<null>> {
  return post('/v1/auth/change-password', { oldPassword, newPassword })
}
