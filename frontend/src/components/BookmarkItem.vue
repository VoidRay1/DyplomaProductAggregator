<template>
  <div>
    <q-card
      flat
      bordered
    >
      <q-card-section class="product-card text-center">
        <router-link
          :to="product.url"
          style="text-decoration: none"
        >
          <q-img
            :src="product.image"
            class="product-image"
            fit="contain"
          />
          <div class="text-subtitle1 text-grey-8 q-mt-sm">{{ product.name }}</div>
        </router-link>
      </q-card-section>
    </q-card>
  </div>
</template>
  
<script setup>
const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})
</script>
  
<style lang="sass" scoped>
.product-card
  width: 100%
  max-width: 210px
  max-height: 360px
.product-image
  width: 170px
  height: 250px
  min-width: 20px
  min-height: 20px
</style>