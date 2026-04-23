import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  // Public routes
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/views/public/HomeView.vue'),
        meta: { title: 'Home' },
      },
      {
        path: 'articles',
        name: 'articles',
        component: () => import('@/views/public/ArticlesView.vue'),
        meta: { title: 'Articles' },
      },
      {
        path: 'articles/:id',
        name: 'article-detail',
        component: () => import('@/views/public/ArticleDetailView.vue'),
        meta: { title: 'Article' },
      },
      {
        path: 'archive',
        name: 'archive',
        component: () => import('@/views/public/ArchiveView.vue'),
        meta: { title: 'Archive' },
      },
      {
        path: 'archive/:volumeId/issues/:issueId',
        name: 'issue',
        component: () => import('@/views/public/IssueView.vue'),
        meta: { title: 'Issue' },
      },
      {
        path: 'editorial-board',
        name: 'editorial-board',
        component: () => import('@/views/public/EditorialBoardView.vue'),
        meta: { title: 'Editorial Board' },
      },
      {
        path: 'contact',
        name: 'contact',
        component: () => import('@/views/public/ContactView.vue'),
        meta: { title: 'Contact' },
      },
      {
        path: 'search',
        name: 'search',
        component: () => import('@/views/public/SearchView.vue'),
        meta: { title: 'Search' },
      },
      {
        path: 'conferences',
        name: 'conferences',
        component: () => import('@/views/public/ConferencesView.vue'),
        meta: { title: 'Konferensiyalar' },
      },
      {
        path: 'conferences/:id',
        name: 'conference-detail',
        component: () => import('@/views/public/ConferenceDetailView.vue'),
        meta: { title: 'Konferensiya' },
      },
      {
        path: 'pages/:slug',
        name: 'static-page',
        component: () => import('@/views/public/StaticPageView.vue'),
      },
    ],
  },

  // Auth routes
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: 'Sign In', guestOnly: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { title: 'Register', guestOnly: true },
  },
  {
    path: '/verify-email',
    name: 'verify-email',
    component: () => import('@/views/auth/VerifyEmailView.vue'),
    meta: { title: 'Verify Email' },
  },
  {
    path: '/email-confirmed',
    name: 'email-confirmed',
    component: () => import('@/views/auth/EmailConfirmedView.vue'),
    meta: { title: 'Email Confirmed' },
  },

  // Author routes
  {
    path: '/author',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true, roles: ['author', 'editor', 'reviewer', 'superadmin'] },
    children: [
      {
        path: 'dashboard',
        name: 'author-dashboard',
        component: () => import('@/views/author/AuthorDashboard.vue'),
        meta: { title: 'Dashboard' },
      },
      {
        path: 'articles',
        name: 'my-articles',
        component: () => import('@/views/author/MyArticlesView.vue'),
        meta: { title: 'My Articles' },
      },
      {
        path: 'articles/:id',
        name: 'article-status',
        component: () => import('@/views/author/ArticleStatusView.vue'),
        meta: { title: 'Article Status' },
      },
      {
        path: 'profile',
        name: 'author-profile',
        component: () => import('@/views/author/AuthorProfileView.vue'),
        meta: { title: 'My Profile' },
      },
    ],
  },

  // Reviewer routes
  {
    path: '/reviewer',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true, roles: ['reviewer', 'editor', 'superadmin'] },
    children: [
      {
        path: 'dashboard',
        name: 'reviewer-dashboard',
        component: () => import('@/views/reviewer/ReviewerDashboard.vue'),
        meta: { title: 'Reviewer Dashboard' },
      },
      {
        path: 'articles/:reviewId',
        name: 'review-article',
        component: () => import('@/views/reviewer/ReviewArticleView.vue'),
        meta: { title: 'Review Article' },
      },
      {
        path: 'review/:reviewId',
        name: 'reviewer-review',
        component: () => import('@/views/reviewer/ReviewArticleView.vue'),
        meta: { title: 'Write Review' },
      },
    ],
  },

  // Admin routes
  {
    path: '/admin',
    component: () => import('@/components/layout/AdminLayout.vue'),
    meta: { requiresAuth: true, roles: ['editor', 'superadmin'] },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard',
      },
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: () => import('@/views/admin/AdminDashboard.vue'),
        meta: { title: 'Boshqaruv paneli' },
      },
      {
        path: 'articles',
        name: 'admin-articles',
        component: () => import('@/views/admin/AdminArticlesView.vue'),
        meta: { title: 'Maqolalar' },
      },
      {
        path: 'articles/new',
        name: 'admin-article-new',
        component: () => import('@/views/admin/AdminArticleFormView.vue'),
        meta: { title: 'Yangi maqola' },
      },
      {
        path: 'articles/:id/edit',
        name: 'admin-article-edit',
        component: () => import('@/views/admin/AdminArticleFormView.vue'),
        meta: { title: 'Maqolani tahrirlash' },
      },
      {
        path: 'articles/:id/review',
        name: 'admin-article-review',
        component: () => import('@/views/admin/AdminArticleReviewView.vue'),
        meta: { title: 'Taqrizni boshqarish' },
      },
      {
        path: 'volumes',
        name: 'admin-volumes',
        component: () => import('@/views/admin/AdminVolumesView.vue'),
        meta: { title: 'Jildlar va sonlar' },
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/views/admin/AdminUsersView.vue'),
        meta: { title: 'Foydalanuvchilar' },
      },
      {
        path: 'editorial',
        name: 'admin-editorial',
        component: () => import('@/views/admin/AdminEditorialView.vue'),
        meta: { title: 'Tahririyat kengashi' },
      },
      {
        path: 'editorial/new',
        name: 'admin-editorial-new',
        component: () => import('@/views/admin/AdminEditorialFormView.vue'),
        meta: { title: 'Yangi a\'zo' },
      },
      {
        path: 'editorial/:id/edit',
        name: 'admin-editorial-edit',
        component: () => import('@/views/admin/AdminEditorialFormView.vue'),
        meta: { title: 'A\'zoni tahrirlash' },
      },
      {
        path: 'pages',
        name: 'admin-pages',
        component: () => import('@/views/admin/AdminPagesView.vue'),
        meta: { title: 'Statik sahifalar' },
      },
      {
        path: 'announcements',
        name: 'admin-announcements',
        component: () => import('@/views/admin/AdminAnnouncementsView.vue'),
        meta: { title: 'E\'lonlar' },
      },
      // Conference management — alohida sahifalar
      {
        path: 'conf/list',
        name: 'admin-conf-list',
        component: () => import('@/views/admin/AdminConfListView.vue'),
        meta: { title: 'Konferensiyalar' },
      },
      {
        path: 'conf/list/new',
        name: 'admin-conf-create',
        component: () => import('@/views/admin/AdminConfEditView.vue'),
        meta: { title: 'Yangi konferensiya' },
      },
      {
        path: 'conf/list/:id/edit',
        name: 'admin-conf-edit',
        component: () => import('@/views/admin/AdminConfEditView.vue'),
        meta: { title: 'Konferensiyani tahrirlash' },
      },
      {
        path: 'conf/sessions',
        name: 'admin-conf-sessions',
        component: () => import('@/views/admin/AdminConfSessionsView.vue'),
        meta: { title: 'Sonlar' },
      },
      // Conference papers (xuddi articles dek)
      {
        path: 'conferences',
        name: 'admin-conferences',
        component: () => import('@/views/admin/AdminConferencesView.vue'),
        meta: { title: 'Konferensiya maqolalari' },
      },
      {
        path: 'conferences/new',
        name: 'admin-conference-new',
        component: () => import('@/views/admin/AdminConferenceFormView.vue'),
        meta: { title: 'Yangi maqola' },
      },
      {
        path: 'conferences/:id/papers/:paperId/edit',
        name: 'admin-conference-paper-edit',
        component: () => import('@/views/admin/AdminConferenceFormView.vue'),
        meta: { title: 'Maqolani tahrirlash' },
      },
      {
        path: 'home-settings',
        name: 'admin-home-settings',
        component: () => import('@/views/admin/AdminHomeSettingsView.vue'),
        meta: { title: 'Bosh sahifa sozlamalari' },
      },
      {
        path: 'categories',
        name: 'admin-categories',
        component: () => import('@/views/admin/AdminCategoriesView.vue'),
        meta: { title: 'Kategoriyalar' },
      },
      {
        path: 'indexing',
        name: 'admin-indexing',
        component: () => import('@/views/admin/AdminIndexingView.vue'),
        meta: { title: 'Indekslash bazalari' },
      },
    ],
  },

  // Error pages
  {
    path: '/error',
    name: 'error',
    component: () => import('@/views/errors/ErrorView.vue'),
    meta: { title: 'Error' },
  },

  // 404 catch-all
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/errors/NotFoundView.vue'),
    meta: { title: '404 Not Found' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0, behavior: 'smooth' }
  },
})

// Navigation guards
router.beforeEach(async (to, _from, next) => {
  // Set page title. The actual journal name is appended later by useSeoMeta
  // once the site-info store is loaded; fall back to the route title or generic brand.
  const title = to.meta.title as string | undefined
  document.title = title || 'Academicbook'

  const token = localStorage.getItem('access_token')
  const isAuthenticated = !!token

  // Redirect authenticated users away from guest-only pages
  if (to.meta.guestOnly && isAuthenticated) {
    return next({ name: 'home' })
  }

  // Require authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  next()
})

export default router
