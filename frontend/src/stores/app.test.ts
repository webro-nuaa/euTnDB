import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAppStore } from '@/stores/app'

describe('App Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with default values', () => {
    const store = useAppStore()
    expect(store.sidebarCollapsed).toBe(false)
    expect(store.loading).toBe(false)
    expect(store.theme).toBe('light')
  })

  it('toggleSidebar switches state', () => {
    const store = useAppStore()
    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(true)
    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(false)
  })

  it('setLoading updates loading state', () => {
    const store = useAppStore()
    store.setLoading(true)
    expect(store.loading).toBe(true)
    store.setLoading(false)
    expect(store.loading).toBe(false)
  })

  it('setTheme updates theme and DOM attribute', () => {
    const store = useAppStore()
    store.setTheme('dark')
    expect(store.theme).toBe('dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })
})
