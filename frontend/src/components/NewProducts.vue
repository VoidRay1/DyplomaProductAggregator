<template>
  <q-card
    bordered
    class="my-card"
  >
    <q-card-section>
      <div class="text-h5">{{ __('New products') }}</div>
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
      <q-carousel-slide v-for="(products, index) in newProducts"
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
            @click="showProduct(product)"
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
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useQuery } from '@vue/apollo-composable'
import { NEW_PRODUCTS } from '../constants/graphql'

const slide = ref(0)
const size = 5

const { result, loading, error } = useQuery(NEW_PRODUCTS, {})
const items = computed(() => result.value?.newProducts ?? [])

const newProducts = computed(() => {
  const products = reactive([])
  for (let i = 0; i < Math.ceil(items.value.length / size); i++) {
    products.push(items.value.slice((i * size), (i * size) + size))
  }
  return products
})

const imageUrl = (path) => { return process.env.MEDIA_URI + path }
</script>

<style lang="sass" scoped>
.carousel
  background-color: white
  height: 300px
.title
  white-space: nowrap
  overflow: hidden
  text-overflow: ellipsis
  width: 140px
  padding: 0 5px  
</style>