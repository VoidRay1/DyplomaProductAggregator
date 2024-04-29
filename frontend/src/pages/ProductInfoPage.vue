<template>
<div class="flex flex-center q-pa-ms">
    <LoadingSpinner v-if="loading" />
    <div v-else-if="error">
      Error: {{ error.message }}
    </div>
      <q-card class="my-card">
        <q-card-section>
          <div class="text-h5">{{ product.name }}</div>
        </q-card-section>
        <q-separator />
        <q-card-section class="q-gutter-md">
          <div>
            <ProductItem :product="product" :isShopProductUrl="true" />
          </div>
        </q-card-section>
      </q-card>
  <q-card v-if="historyProducts.length > 0"
    bordered
    class="my-card"
  >
  <q-card-section>
      <div class="text-h5">{{ __('User product history') }}</div>
  </q-card-section>
  <q-separator />
  <q-carousel
      v-model="slide"
      transition-prev="slide-right"
      transition-next="slide-left"
      swipeable
      animated
      control-color="orange"
      :autoplay="false"
      :navigation="true"
      :arrows="true"
      padding
      infinite
      class="carousel"
    >
      <q-carousel-slide v-for="(products, index) in historyProducts"
        :key="index"
        :name="index"
        class="column no-wrap"
      >
        <div class="row fit justify-start items-center q-gutter-sm q-col-gutter no-wrap">
          <q-img v-for="product in products"
            :key="product.id"
            :src="product.image"
            class="rounded-borders full-height"
            fit="contain"
            style="background-color: white; cursor: pointer; border: 1px solid #e0e0e0;"
            img-class="q-pa-sm"
            @click="showProductInfoPage(product)"
          >
            <q-badge
              color="orange-4"
              :label="Math.round(product.price.price).toLocaleString() + ' ₴'"
              style="top: 8px; left: 8px; background-color: transparent; padding: 5px;"
            />
            <q-avatar square style="top: -10px; right: 18px; background-color: transparent; padding: 5px;">
              <q-img :src="imageUrl(product.shop.image)" fit="scale-down" />
            </q-avatar>
            <div class="absolute-bottom row q-pa-none">
              <div class="text-center justify-center title">
                {{ product.name }}
              </div>
            </div>
          </q-img>
        </div>
      </q-carousel-slide>
    </q-carousel>
  </q-card>
  </div>
</template>
  
<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router' 
import { GET_PRODUCT } from '../constants/graphql'
import { useQuery } from '@vue/apollo-composable'
import { useRoute } from 'vue-router'
import { useGettext } from 'vue3-gettext'
import ProductItem from 'components/ProductItem.vue'
import LoadingSpinner from 'components/LoadingSpinner.vue'
import { GET_HISTORY_PRODUCTS } from '../constants/graphql'

const route = useRoute()
const router = useRouter()

const {
  result: getProduct,
  loading,
  error
} = useQuery(GET_PRODUCT, () => ({ slug: route.params.productSlug }))

const { result: getHistoryProducts } = useQuery(GET_HISTORY_PRODUCTS,  {})

const product = computed(() => getProduct.value?.product ?? [])

const historyProductsResult = computed(() => getHistoryProducts.value?.historyProducts ?? [])

const imageUrl = (path) => { return process.env.MEDIA_URI + path }

const slide = ref(0)
const size = 5
const { current } = useGettext()
const language = localStorage.getItem('language') || current

const historyProducts = computed(() => {
  const products = reactive([])
  for (let i = 0; i < Math.ceil(historyProductsResult.value.length / size); i++) {
    products.push(historyProductsResult.value.slice((i * size), (i * size) + size))
  }
  return products
})
      
function showProductInfoPage(product){
  router.push({
    name: 'productInfo',
    params: {
      productSlug: product.productSlug
    }
  })
}

</script>
<style lang="sass" scoped>
.carousel
  background-color: white
  height: 300px
.title
  white-space: nowrap
  overflow: hidden
  text-overflow: ellipsis
  width: 270px
  padding: 0 5px  
</style>