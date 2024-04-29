<template>
  <q-card-section horizontal>
    <q-card-section class="col-3 flex text-center q-pa-sm">
      <router-link :to="{ name: 'productInfo', params: { productSlug: product.productSlug } }" style="text-decoration: none;">
      <!-- <a
        :href="product.url"
        target="_blank"
        style="text-decoration: none;"
      > -->
        <q-img
          :src="product.image"
          class="product-image"
          fit="contain"
        />
        <div class="text-subtitle1 text-center text-grey q-mt-sm">{{ product.name }}</div>
        <q-chip outline color="orange" text-color="white">{{ Math.round(product.price.price).toLocaleString() }} ₴</q-chip>
      </router-link>
        <!-- </a> -->
    </q-card-section>

    <q-card-section class="flex flex-top q-pa-sm">
      <div v-for="product in similarProducts"
        :key="product.node.id"
        class="similar-product q-pb-md"
      >
        <SimilarProduct :product="product.node" :isShopProductUrl="isShopProductUrl" />
      </div>
    </q-card-section>
  </q-card-section>
</template>

<script setup>
import { RouterLink } from 'vue-router' 
import { computed } from 'vue'
import { useGettext } from 'vue3-gettext'
import SimilarProduct from 'components/SimilarProduct.vue'
import { useQuery } from '@vue/apollo-composable'
import { GET_SIMILAR_PRODUCTS } from '../constants/graphql'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
  isShopProductUrl: {
    type: Boolean,
    required: true
  }
})

const { current } = useGettext()
const language = localStorage.getItem('language') || current

const {
  result,
  loading,
  error
} = useQuery(GET_SIMILAR_PRODUCTS, () => ({product: props.product.id}))

const similarProducts = computed(() => result.value?.similarProducts.edges ?? [])

const imageUrl = (path) => { return process.env.MEDIA_URI + path }
</script>

<style lang="sass" scoped>
.product-image
  width: 120px
  max-height: 240px
  min-width: 20px
  min-height: 20px
.similar-product
  position: relative
  display: inline-block
  vertical-align: top
  margin-left: 35px
</style>