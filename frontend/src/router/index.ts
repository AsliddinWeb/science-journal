import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  // Public routes — all live under the admin-configurable :journalSlug.
  // beforeEach below redirects "/" and bare "/articles", "/archive", … to
  // the slug-prefixed equivalents so old links don't break.
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    children: [
      {
        path: ':journalSlug',
        children: [
          // ── OJS-canonical public routes ──
          // Mirror the URL shape used by OJS-based journals
          // (e.g. publishscience.uz/sirsh/index, /article/view/:id,
          // /issue/view/:id, /about/editorialTeam). Google Scholar's
          // platform fingerprint recognises this layout.
          { path: '', redirect: (to) => ({ path: `/${to.params.journalSlug}/index`, query: to.query, hash: to.hash }) },
          {
            path: 'index',
            name: 'journal-home',
            component: () => import('@/views/public/HomeView.vue'),
            meta: { title: 'Home' },
          },
          {
            path: 'article/view/:id',
            name: 'article-detail',
            component: () => import('@/views/public/ArticleDetailView.vue'),
            meta: { title: 'Article' },
          },
          {
            path: 'article/view/:id/:galleyId',
            name: 'article-galley',
            component: () => import('@/views/public/ArticleDetailView.vue'),
            meta: { title: 'Article' },
          },
          {
            path: 'issue/archive',
            name: 'archive',
            component: () => import('@/views/public/ArchiveView.vue'),
            meta: { title: 'Archive' },
          },
          {
            path: 'issue/current',
            name: 'issue-current',
            component: () => import('@/views/public/ArchiveView.vue'),
            meta: { title: 'Current Issue' },
          },
          {
            path: 'issue/view/:issueId',
            name: 'issue',
            component: () => import('@/views/public/IssueView.vue'),
            meta: { title: 'Issue' },
          },
          {
            path: 'about',
            name: 'about',
            component: () => import('@/views/public/StaticPageView.vue'),
            props: () => ({ slug: 'about' }),
            meta: { title: 'About' },
          },
          {
            path: 'about/editorialTeam',
            name: 'editorial-board',
            component: () => import('@/views/public/EditorialBoardView.vue'),
            meta: { title: 'Editorial Board' },
          },
          {
            path: 'about/contact',
            name: 'contact',
            component: () => import('@/views/public/ContactView.vue'),
            meta: { title: 'Contact' },
          },
          {
            path: 'about/submissions',
            name: 'submissions',
            component: () => import('@/views/public/StaticPageView.vue'),
            props: () => ({ slug: 'author-guidelines' }),
            meta: { title: 'Submissions' },
          },
          {
            path: 'about/editorialPolicies',
            name: 'editorial-policies',
            component: () => import('@/views/public/StaticPageView.vue'),
            props: () => ({ slug: 'peer-review' }),
            meta: { title: 'Editorial Policies' },
          },
          {
            path: 'about/privacy',
            name: 'privacy',
            component: () => import('@/views/public/StaticPageView.vue'),
            props: () => ({ slug: 'privacy' }),
            meta: { title: 'Privacy Statement' },
          },
          {
            path: 'about/aboutThisPublishingSystem',
            redirect: (to) => ({ path: `/${to.params.journalSlug}/about` }),
          },

          // Articles browse — kept at /articles since OJS doesn't have a
          // direct equivalent (OJS only has search). Listed in sitemap.
          {
            path: 'articles',
            name: 'articles',
            component: () => import('@/views/public/ArticlesView.vue'),
            meta: { title: 'Articles' },
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
          // Legacy paths (articles/<id>, archive/...) are NOT added here as
          // route-level redirects on purpose: a redirect under :journalSlug
          // wouldn't know the real slug if the URL came in without one
          // (the :journalSlug param would bind to the literal first segment
          // like 'articles' or 'about' and the redirect would loop). All
          // legacy → OJS-canonical mapping is done in beforeEach below,
          // where the configured slug is always available from siteInfo.
        ],
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

// Top-level segments that are NOT journal slugs (must never be mistaken for one).
const RESERVED_TOP_LEVEL = new Set([
  'admin', 'author', 'reviewer', 'login', 'register',
  'verify-email', 'email-confirmed', 'error',
  'api', 'sitemap.xml', 'robots.txt', 'prerender', 'oai',
])

// First-segments that look like a slug to Vue Router's :journalSlug param
// but are really OJS path components or legacy public paths. When we see
// one of these as the first URL segment, we know the slug was missing and
// we prepend it.
const PUBLIC_TOP_SEGMENTS = new Set([
  // OJS-canonical first segments
  'article', 'issue', 'about', 'index',
  // Legacy public first segments
  'articles', 'archive', 'editorial-board', 'contact', 'search',
  'conferences', 'pages',
])

// Map legacy URL shapes to their OJS-canonical equivalent. `segs` is the
// path split on '/' with the slug already stripped, so for the URL
// `/fif/articles/abc` we receive segs = ['articles', 'abc']. Returns the
// new segments array (under the slug) or null when no rewrite applies.
function rewriteLegacy(segs: string[]): string[] | null {
  if (segs.length === 2 && segs[0] === 'articles') {
    // /<slug>/articles/<id> → /<slug>/article/view/<id>
    return ['article', 'view', segs[1]]
  }
  if (segs.length === 1 && segs[0] === 'archive') {
    // /<slug>/archive → /<slug>/issue/archive
    return ['issue', 'archive']
  }
  if (segs.length === 4 && segs[0] === 'archive' && segs[2] === 'issues') {
    // /<slug>/archive/<volumeId>/issues/<issueId> → /<slug>/issue/view/<issueId>
    return ['issue', 'view', segs[3]]
  }
  if (segs.length === 1 && segs[0] === 'editorial-board') {
    return ['about', 'editorialTeam']
  }
  if (segs.length === 1 && segs[0] === 'contact') {
    return ['about', 'contact']
  }
  return null
}

// Navigation guards
router.beforeEach(async (to, _from, next) => {
  // Set page title. The actual journal name is appended later by useSeoMeta
  // once the site-info store is loaded; fall back to the route title or generic brand.
  const title = to.meta.title as string | undefined
  document.title = title || 'Academicbook'

  const token = localStorage.getItem('access_token')
  const isAuthenticated = !!token

  // Resolve journal slug (from siteInfo, default fallback).
  let slug = 'academic-book-journal'
  try {
    const { useSiteInfoStore } = await import('@/stores/siteInfo')
    const siteInfo = useSiteInfoStore()
    if (!siteInfo.loaded) await siteInfo.load()
    slug = siteInfo.journalSlug || slug
  } catch { /* fall through with default */ }

  const path = to.path

  // "/" → "/{slug}/index" (OJS-canonical home, single hop)
  if (path === '/') {
    return next({ path: `/${slug}/index${to.hash || ''}`, query: to.query, replace: true })
  }

  const segs = path.split('/').filter(Boolean)
  const firstSeg = segs[0] || ''

  // No-slug public URL: prepend slug, and apply any legacy → OJS rewrite
  // in the same hop so we converge on the canonical form immediately.
  if (PUBLIC_TOP_SEGMENTS.has(firstSeg)) {
    const rewritten = rewriteLegacy(segs)
    const newSegs = rewritten ?? segs
    return next({
      path: `/${slug}/${newSegs.join('/')}${to.hash || ''}`,
      query: to.query,
      replace: true,
    })
  }

  // Already slug-prefixed: detect legacy paths inside the slug and rewrite
  // to the OJS form (e.g. /fif/articles/abc → /fif/article/view/abc).
  if (firstSeg === slug && segs.length >= 2) {
    const rewritten = rewriteLegacy(segs.slice(1))
    if (rewritten) {
      return next({
        path: `/${slug}/${rewritten.join('/')}${to.hash || ''}`,
        query: to.query,
        replace: true,
      })
    }
  }

  // Bare /<slug> (no trailing /index) → land on /index
  if (firstSeg === slug && segs.length === 1) {
    return next({ path: `/${slug}/index${to.hash || ''}`, query: to.query, replace: true })
  }

  // Different slug than the configured one (e.g. user has bookmarked the
  // old slug): swap to the configured slug, preserving the rest of the URL.
  if (
    firstSeg
    && !RESERVED_TOP_LEVEL.has(firstSeg)
    && firstSeg !== slug
    && to.matched.some(r => r.path.startsWith('/:journalSlug'))
  ) {
    const rest = path.slice(firstSeg.length + 1) // strip "/<wrongSlug>"
    return next({ path: `/${slug}${rest}${to.hash || ''}`, query: to.query, replace: true })
  }

  // Redirect authenticated users away from guest-only pages
  if (to.meta.guestOnly && isAuthenticated) {
    return next({ path: `/${slug}/index` })
  }

  // Require authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  next()
})

export default router
