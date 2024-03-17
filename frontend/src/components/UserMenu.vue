<template>
    <div>
      <q-avatar v-if="token.isAuthenticated">
        <img v-if="user" :src="getAvatar(user.profile?.avatar)">
        <q-menu
          transition-show="scale"
          transition-hide="scale"
        >
          <q-list style="min-width: 100px" class="text-orange">
            <q-item
              clickable
              to="/profile"
              active-class="bg-orange-2"
            >
              <q-item-section avatar>
                <q-icon name="person" />
              </q-item-section>
              <q-item-section>{{ __('Profile') }}</q-item-section>
            </q-item>
            <q-item
              clickable
              to="/settings"
              active-class="bg-orange-2"
            >
              <q-item-section avatar>
                <q-icon name="settings" />
              </q-item-section>
              <q-item-section>{{ __('Settings') }}</q-item-section>
            </q-item>
            <q-separator />
            <q-item
              clickable
              v-close-popup
              @click="logoutUser"
            >
              <q-item-section avatar>
                <q-icon name="logout" />
              </q-item-section>
              <q-item-section>{{ __('Logout') }}</q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-avatar>
    </div>    
</template>
  
<script setup>
import { useQuasar } from 'quasar'
import { computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTokenStore } from 'stores/token'
import { useUserStore } from 'stores/user'
import { useGettext } from 'vue3-gettext'
import { useQuery, useMutation } from '@vue/apollo-composable'
import { GET_USER, REVOKE_TOKEN } from '../constants/graphql'

const $q = useQuasar()
const router = useRouter()
const token = useTokenStore()
const userStore = useUserStore()
const { $gettext } = useGettext()
    
token.initialize()

const { result } = useQuery(GET_USER)
const user = computed(() => result.value?.viewer ?? {})

watch(user, () => {
  if (token.isAuthenticated && result.value) {
    if (!userStore.user) {
      userStore.setUser(user.value)
    } 
  }
})

function triggerPositive () {
  $q.notify({
    type: 'positive',
    message: $gettext('Logout successful')
  })
}

function triggerNegative (message) {
  $q.notify({
    type: 'negative',
    message: message
  })
}

const { mutate: logoutUser, onDone, onError } = useMutation(REVOKE_TOKEN, () => ({
  variables: {
    refreshToken: localStorage.getItem('refresh_token')
  }
}))

onDone((response) => {
  if (response.errors) {
    triggerNegative(response.errors)
  }
  if (response.data?.revokeToken.revoked) {
    token.removeToken()
    triggerPositive()
    router.push('/')
  }
})
  
onError(error => {
  console.log(error)
//  triggerNegative(error.response.errors)
})

const getAvatar = (path) => {
  if (path) {
    return process.env.MEDIA_URI + path
  } else {
    return "/src/assets/avatar-icon.svg"
  }
}
</script>