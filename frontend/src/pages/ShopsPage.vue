<template>
  <q-page class="flex flex-center content-start">
    <q-card class="my-card">
      <q-card-section class="flex row items-center q-py-sm">
        <div class="col-2 text-h5">{{ __('Shops') }}</div>
      </q-card-section>
      <q-separator />
      <q-card-section class="q-pa-none">
        <q-tabs
          v-model="selectedShopTab"
          narrow-indicator
          dense
        >
          <q-tab v-for="shop in shops"
            :key="shop.id"
            :name="shop.id"
            class="text-orange"
          >
            <img
              :src="imageUrl(shop.image)"
              :title="shop.title"
            />
          </q-tab>
        </q-tabs>
        <q-tab-panels v-model="selectedShopTab" animated>
          <q-tab-panel v-for="shop in shops"
            :key="shop.id"
            :name="shop.id"
          >
            <ShopProductList :shop="shop" />
          </q-tab-panel>
        </q-tab-panels>
      </q-card-section>
    </q-card>
  </q-page>
</template>
  
<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from 'stores/user'
import { useGettext } from 'vue3-gettext'
import ShopProductList from 'components/ShopProductList.vue'
import { useQuery } from '@vue/apollo-composable'
import { GET_SHOPS } from '../constants/graphql'

const selectedShopTab = ref('U2hvcE5vZGU6MQ==')
const query = ref('')

const userStore = useUserStore()
const { current } = useGettext()
const language = localStorage.getItem('language') || current

const { result: getShops } = useQuery(GET_SHOPS, {
  country: userStore.user?.country ?? 'UA',
  language: language
})

const shops = computed(() => getShops.value?.shops ?? [])

const imageUrl = (path) => { return process.env.MEDIA_URI + path }
</script>
