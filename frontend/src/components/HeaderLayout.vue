<template>
  <div class="bg-cyan text-white">
    <q-header
      reveal
      elevated
      class="header"
    >
      <q-toolbar class="row justify-between q-mb-sm">
        <div class="flex">
          <q-btn
            flat
            dense
            round
            icon="menu"
            aria-label="Menu"
            @click="toggleLeftDrawer"
            class="xs"
          />
          <router-link to="/">
            <img src="~assets/logo.svg" class="absolute-left q-ma-sm logo">
          </router-link>
        </div>
        <div class="flex items-center q-pt-sm q-gutter-sm">
          <q-form
            :action="`/cocktails/${language}`"
            method="GET"
          >
            <q-input
              dark
              rounded
              dense
              standout
              v-model="searchText"
              name="q"
              input-class="text-left"
              class=""
            >
              <template v-slot:prepend>
                <q-icon v-if="searchText === ''" name="search" />
                <q-icon v-else name="clear" class="cursor-pointer" @click="searchText = ''" />
              </template>
            </q-input>
          </q-form>
          <!--q-btn flat round icon="settings_brightness" class="q-mr-xs" @click="toggleDark" /-->
          <UserMenu v-if="token.isAuthenticated" />
          <q-btn v-show="!token.isAuthenticated"
            flat
            round
            icon="login"
            class="q-mr-xs"
            @click="loginForm = true"
          >
            <q-tooltip class="bg-orange">{{ __('Login') }}</q-tooltip>
          </q-btn>
          <LanguageSelect />
          <LoginForm v-model="loginForm" />
        </div>
      </q-toolbar>
 
      <q-tabs
        class="gt-xs text-orange"
      >
        <q-route-tab name="home" :label="__('Home')" to="/" />
       <q-route-tab v-show="token.isAuthenticated" name="shops" :label="__('Shops')" to="/shops" />
      </q-tabs>
    </q-header>
  </div>
</template>

<script setup>
//import { Dark } from 'quasar'
import { ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import { useTokenStore } from 'stores/token'
import LoginForm from 'components/LoginForm.vue'
import UserMenu from 'components/UserMenu.vue'
import LanguageSelect from 'components/LanguageSelect.vue'

const emit = defineEmits(['my-switchLeftDrawer'])

const { current } = useGettext()
const language = localStorage.getItem('language') || current

const token = useTokenStore()
token.initialize()

const searchText = ref('')
const loginForm = ref(false)

const toggleLeftDrawer = () => { emit('my-switchLeftDrawer') }
//const toggleDark = () => { Dark.toggle() }
</script>

<style lang="sass" scoped>
.header
  background-color: $blue-grey-10
.logo
  width: 80px
  @media (max-width: $breakpoint-sm-max)
    width: 50px
  @media (max-width: $breakpoint-xs-max)
    display: none
</style>