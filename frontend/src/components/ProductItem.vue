<template>
  <q-card-section horizontal>
    <q-card-section class="col-3 flex text-center q-pa-sm">
      <a
        :href="product.url"
        target="_blank"
        style="text-decoration: none;"
      >
        <q-img
          :src="product.image"
          class="product-image"
          fit="contain"
        />
        <div class="text-subtitle1 text-center text-grey q-mt-sm">{{ product.name }}</div>
        <q-chip outline color="orange" text-color="white">{{ Math.round(product.price.price).toLocaleString() }} ₴</q-chip>
      </a>
    </q-card-section>

    <q-card-section class="flex flex-top q-pa-sm">
      <div v-for="item in similars"
        :key="item.node.id"
        class="similar-item q-pb-md"
      >
        <SimilarItem :product="item.node" />
      </div>
    </q-card-section>
  </q-card-section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useGettext } from 'vue3-gettext'
import SimilarItem from 'components/SimilarItem.vue'
import { useQuery } from '@vue/apollo-composable'
import { GET_SIMILAR_PRODUCTS } from '../constants/graphql'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  }
})

const { current } = useGettext()
const language = localStorage.getItem('language') || current

const {
  result,
  loading,
  error
} = useQuery(GET_SIMILAR_PRODUCTS, () => ({product: props.product.id}))
      
const similars = computed(() => result.value?.similarProducts.edges ?? [])

const imageUrl = (path) => { return process.env.MEDIA_URI + path }
</script>

<style lang="sass" scoped>
.product-image
  width: 120px
  max-height: 240px
  min-width: 20px
  min-height: 20px
.similar-item
  position: relative
  display: inline-block
  vertical-align: top
  margin-left: 35px
</style>