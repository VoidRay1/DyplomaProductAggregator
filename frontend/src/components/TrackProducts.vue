<template>
  <div class="flex flex-center q-pa-ms">
    <LoadingSpinner v-if="loading" />
    <div v-else-if="error">
      Error: {{ error.message }}
    </div>
      <q-card class="my-card" v-if="products.length > 0">
        <q-card-section>
          <div class="text-h5">{{ __('My products') }}</div>
        </q-card-section>
        <q-separator />
        <q-card-section class="q-gutter-md">
          <div v-for="product in products"
            :key="product.node.id"
          >
            <ProductItem :product="product.node" :isShopProductUrl="isShopProductUrl" />
            <q-separator />
          </div>
          <!-- <q-intersection
            v-for="item in products"
            :key="item.node.id"
            once
            transition="scale"
            transition-duration="700"
            class="product text-center"
            @mouseenter="show = item.node.id"
            @mouseleave="show = false"
            @click="showProduct(item.node)"
          >
             -->
            <!-- <q-img
              :src="item.node.image"
              fit="contain"
              img-class="q-pa-sm"
              style="width: 120px; height: 200px; background-color: transparent;"
            />
            <div class="text-subtitle2 text-grey text-center title">
              {{ item.node.name }}
            </div>   -->
          <!-- </q-intersection>
          <div v-if="products.length < 6" style="width: 960px;" /> -->
        </q-card-section>
      </q-card>
  </div>
</template>
    
<script setup>
import { useQuasar } from 'quasar'
import { ref, computed } from 'vue'
import { useGettext } from 'vue3-gettext'
import LoadingSpinner from 'components/LoadingSpinner.vue'
import ProductItem from 'components/ProductItem.vue'
import { useQuery } from '@vue/apollo-composable'
import { GET_TRACK_PRODUCTS } from '../constants/graphql'

const $q = useQuasar()
const { current } = useGettext()
const language = localStorage.getItem('language') || current

const show = ref(false)

const props = defineProps({
  isShopProductUrl: {
    type: Boolean,
    required: true
  }
})

const {
  result,
  loading,
  error
} = useQuery(GET_TRACK_PRODUCTS, () => ({}))
      
const products = computed(() => result.value?.trackProducts.edges ?? [])
</script>
    
<style lang="sass" scoped>
.product
  width: 140px
  height: 240px
  display: inline-block
  border-radius: 20px
  border: 1px solid #ff9800
  cursor: pointer
.title
  white-space: nowrap
  overflow: hidden
  text-overflow: ellipsis
  width: 140px
  padding: 0 5px
</style>