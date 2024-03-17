import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTokenStore = defineStore('token', () => {
  const access_token = ref('')
  const refresh_token = ref('')
  const isAuthenticated = ref(false)

  const initialize = () => {
    if ( localStorage.getItem('access_token') ) {
      access_token.value = localStorage.getItem('access_token')
      refresh_token.value = localStorage.getItem('refresh_token')
      isAuthenticated.value = true
    } else {
      access_token.value = ''
      refresh_token.value = ''
      isAuthenticated.value = false
    }
  }

  const setToken = (tokenAuth) => {
    access_token.value = tokenAuth.token
    refresh_token.value = tokenAuth.refreshToken
    localStorage.setItem('access_token', tokenAuth.token)
    localStorage.setItem('refresh_token', tokenAuth.refreshToken)
    isAuthenticated.value = true
  }

  const removeToken = () => {
    access_token.value = ''
    refresh_token.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    isAuthenticated.value = false
  }

  return {
    access_token,
    refresh_token,
    isAuthenticated,
    initialize,
    setToken,
    removeToken,
  }
})
