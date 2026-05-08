import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'

// Mock the API module
vi.mock('@/api/request', () => ({
  post: vi.fn(),
  get: vi.fn(),
  put: vi.fn(),
  del: vi.fn(),
}))

vi.mock('@/api/auth', () => ({
  logout: vi.fn().mockResolvedValue({ code: 200 }),
}))

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('initializes with no user', () => {
    const store = useUserStore()
    expect(store.isLoggedIn).toBe(false)
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
  })

  it('isLoggedIn returns true when token exists', () => {
    localStorage.setItem('token', 'test-token')
    const store = useUserStore()
    expect(store.isLoggedIn).toBe(true)
  })

  it('isAdmin returns true when user role is admin', () => {
    const store = useUserStore()
    store.setUser({
      id: 1,
      username: 'admin',
      email: 'admin@test.com',
      role: 'admin',
      institution: '',
      is_active: true,
      created_at: '2024-01-01',
    })
    expect(store.isAdmin).toBe(true)
  })

  it('isAdmin returns false for regular user', () => {
    const store = useUserStore()
    store.setUser({
      id: 2,
      username: 'user',
      email: 'user@test.com',
      role: 'user',
      institution: '',
      is_active: true,
      created_at: '2024-01-01',
    })
    expect(store.isAdmin).toBe(false)
  })

  it('logout clears token and user', async () => {
    const store = useUserStore()
    store.setToken('test-token')
    store.setUser({
      id: 1,
      username: 'admin',
      email: 'admin@test.com',
      role: 'admin',
      institution: '',
      is_active: true,
      created_at: '2024-01-01',
    })

    await store.logout()

    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
  })

  it('setToken updates localStorage', () => {
    const store = useUserStore()
    store.setToken('new-token')
    expect(localStorage.getItem('token')).toBe('new-token')
  })
})
