import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const preferences = ref(null)

  const setUser = (userData) => {
    var preferencesMap = new Map()
    for (var i = 0; i < userData.preferences.length; i++) {
      var key = userData.preferences[i].section + '.' + userData.preferences[i].name
      preferencesMap.set(key, userData.preferences[i].value)
    }
    preferences.value = preferencesMap
    user.value = {
      username: userData.username,
      email: userData.email,
      phone: userData.phone,
      avatar: userData.profile.avatar,
      firstName: userData.profile.firstName,
      lastName: userData.profile.lastName,
      dateOfBirth: userData.profile.dateOfBirth,
      country: userData.profile.country,
      telegramUsername: userData.profile.telegramUsername
    }
    localStorage.setItem('userName', user.value.username)
    localStorage.setItem('userAvatar', user.value.avatar)
    localStorage.setItem('userData', JSON.stringify(user.value))
    localStorage.setItem('userPreferences', JSON.stringify(Object.fromEntries(preferences.value)))
  }

  return {
    user,
    preferences,
    setUser,
  }
})
