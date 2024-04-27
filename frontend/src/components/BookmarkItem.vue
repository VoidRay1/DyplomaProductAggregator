<template>
  <!-- <div>
    <q-card
      flat
      bordered
    >
    <div class="product-row">
      <q-card-section class="product-card text-center">
          <q-img
            :src="product.image"
            class="product-image"
            fit="contain"
            style="cursor: pointer;"
            @click="showProductInfoPage(product)"
          />
          <div class="text-subtitle1 text-grey-8 q-mt-sm" style="text-overflow">{{ product.name }}</div>
      </q-card-section>
    </div>
    </q-card>
  </div> -->
  <div class="product-row">
    <q-card class="my-card">
      <q-img
            :src="product.image"
            style="cursor: pointer;"
            @click="showProductInfoPage(product)"
          />

      <q-card-section>
        <div class="absolute-bottom text-subtitle2 text-center">
          {{ product.name }}
        </div>
      </q-card-section>
    </q-card>
    </div>
</template>
  
<script setup>
import { useRouter } from 'vue-router'
const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const router = useRouter()
      
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
.product-card
  width: 100%
  max-width: 250px
  max-height: 360px
.product-image
  width: 170px
  height: 250px
  min-width: 20px
  min-height: 20px
.product-row 
  display: grid
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))
</style>