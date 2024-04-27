import IndexPage from 'pages/IndexPage.vue'
import ShopsPage from 'pages/ShopsPage.vue'
import BookmarksPage from 'pages/BookmarksPage.vue'
import ErrorNotFound from 'pages/ErrorNotFound.vue'

import LoginForm from '../components/LoginForm.vue'
import RegisterForm from '../components/RegisterForm.vue'
import ForgotPassword from '../components/ForgotPassword.vue'
import UserProfile from '../components/UserProfile.vue'
import UserSettings from '../components/UserSettings.vue'
import ProductInfoPage from 'src/pages/ProductInfoPage.vue'

const routes = [
  { 
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: IndexPage },
      { path: 'shops', component: ShopsPage },
      { path: 'product/:productSlug', name: 'productInfo', component: ProductInfoPage },
      { path: 'bookmarks', component: BookmarksPage },
      { path: 'login', component: LoginForm },
      { path: 'register', component: RegisterForm },
      { path: 'forgot', component: ForgotPassword },
      { path: 'profile', component: UserProfile },
      { path: 'settings', component: UserSettings },
    ]
  },
 
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: ErrorNotFound }
    ]
  }
]

export default routes
