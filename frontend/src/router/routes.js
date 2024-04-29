const routes = [
  { 
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('src/pages/HomePage.vue') },
      { path: 'shops', component: () => import('pages/ShopsPage.vue') },
      { path: 'product/:productSlug', name: 'productInfo', component: () => import('src/pages/ProductInfoPage.vue') },
      { path: 'bookmarks', component: () => import('pages/BookmarksPage.vue') },
      { path: 'login', component: () => import('../components/LoginForm.vue') },
      { path: 'register', component: () => import('../components/RegisterForm.vue') },
      { path: 'forgot', component: () => import('../components/ForgotPassword.vue') },
      { path: 'profile', component: () => import('../components/UserProfile.vue') },
      { path: 'settings',  component: () => import('../components/UserSettings.vue') },
    ]
  },
 
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/ErrorNotFound.vue') }
    ]
  }
]

export default routes
