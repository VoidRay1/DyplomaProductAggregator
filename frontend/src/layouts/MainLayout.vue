<template>
  <q-layout view="hHh lPr fFf" class="layout">
    <HeaderLayout @my-switchLeftDrawer="toggleLeftDrawer" />

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above-
      bordered
    >
      <q-list>
        <q-item-label
          header
          overline
        >
          {{ __('Menu') }}
        </q-item-label>
        <q-separator spaced />
        <EssentialLink
          v-for="link in linksList"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
    </q-drawer>

    <q-page-container class="my-container">
      <q-page padding class="my-content">
        
        <router-view :key="route.fullPath" />
        
        <q-page-scroller position="bottom-right" :scroll-offset="150" :offset="[18, 18]">
          <q-btn fab icon="keyboard_arrow_up" color="amber-9" />
        </q-page-scroller>
      </q-page>
    </q-page-container>

    <FooterLayout />
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useGettext } from 'vue3-gettext'
import HeaderLayout from 'components/HeaderLayout.vue'
import FooterLayout from 'components/FooterLayout.vue'
import EssentialLink from 'components/EssentialLink.vue'

const route = useRoute()
const { $gettext, current } = useGettext()
const language = localStorage.getItem('language') || current

const linksList = [
  {
    title: $gettext('Home'),
//    caption: 'main page',
    icon: 'home',
    link: '/'
  },
  {
    title: $gettext('Shops'),
//    caption: 'shops',
    icon: 'shopping_cart',
    link: '/shops'
  },
  {
    title: $gettext('About'),
//    caption: 'about us',
    icon: 'public',
    link: 'about'
  },
]

const leftDrawerOpen = ref(false)
const toggleLeftDrawer = () => { leftDrawerOpen.value = !leftDrawerOpen.value }
</script>

<style lang="sass">
.layout
  font-family: "Montserrat", sans-serif
.my-container
  position: relative
.my-container:before
  content: ' '
  display: block
  position: absolute
  left: 0
  top: 0
  width: 100%
  height: 100%
  opacity: 0.07
  background-size: no-repeat
  background-position: center
.my-content
  position: relative
  border: 10px
.my-card
  width: 100%
  max-width: 960px
.link
  cursor: pointer
  text-decoration: none
  color: $amber-9
.link:hover, .link:focus
  color: $amber-10
</style>