import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/views/public/Layout.vue'),
      children: [
        { path: '', name: 'Home', component: () => import('@/views/public/Home.vue'), meta: { title: 'Home' } },
        { path: 'classification', name: 'Classification', component: () => import('@/views/public/Classification.vue'), meta: { title: 'Classification' } },
        { path: 'search', name: 'Search', component: () => import('@/views/public/Search.vue'), meta: { title: 'Search' } },
        { path: 'tn/:id', name: 'TnDetail', component: () => import('@/views/public/TnDetail.vue'), meta: { title: 'TE Detail' } },
        { path: 'blast', name: 'Blast', component: () => import('@/views/public/Blast.vue'), meta: { title: 'BLAST' } },
        { path: 'submit', name: 'Submit', component: () => import('@/views/public/Submit.vue'), meta: { title: 'Submit' } },
        { path: 'knowledge', name: 'Knowledge', component: () => import('@/views/public/Knowledge.vue'), meta: { title: 'Knowledge Base' } },
        { path: 'help', name: 'Help', component: () => import('@/views/public/Help.vue'), meta: { title: 'Help' } },
      ]
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/public/Login.vue'),
      meta: { title: 'Login' }
    },
    {
      path: '/admin',
      component: () => import('@/views/admin/Layout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { title: 'Dashboard', requiresAuth: true } },
        { path: 'tn', name: 'TnManagement', component: () => import('@/views/admin/TnManagement.vue'), meta: { title: 'TE Management', requiresAuth: true } },
        { path: 'minetn', name: 'MineTnWorkbench', component: () => import('@/views/admin/MineTnWorkbench.vue'), meta: { title: 'MineTn', requiresAuth: true } },
        { path: 'review', name: 'ReviewQueue', component: () => import('@/views/admin/ReviewQueue.vue'), meta: { title: 'Review Queue', requiresAuth: true } },
        { path: 'download-review', name: 'DownloadReview', component: () => import('@/views/admin/DownloadReview.vue'), meta: { title: 'Download Review', requiresAuth: true } },
        { path: 'users', name: 'UserManagement', component: () => import('@/views/admin/UserManagement.vue'), meta: { title: 'User Management', requiresAuth: true } },
        { path: 'settings', name: 'SystemSettings', component: () => import('@/views/admin/SystemSettings.vue'), meta: { title: 'Settings', requiresAuth: true } },
      ]
    }
  ]
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || 'euTnDB'} - euTnDB`
  
  if (to.meta.requiresAuth) {
    const userStore = useUserStore()
    if (!userStore.isLoggedIn) {
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
  }
  next()
})

export default router
