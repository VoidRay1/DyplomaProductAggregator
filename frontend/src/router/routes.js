import IndexPage from 'pages/IndexPage.vue'
import Shops from 'pages/ShopsPage.vue'
import ErrorNotFound from 'pages/ErrorNotFound.vue'

import LoginForm from '../components/LoginForm.vue'
import RegisterForm from '../components/RegisterForm.vue'
import ForgotPassword from '../components/ForgotPassword.vue'
import UserProfile from '../components/UserProfile.vue'
import UserSettings from '../components/UserSettings.vue'

const routes = [
  { 
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: IndexPage },
      { path: 'shops', component: Shops },
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
