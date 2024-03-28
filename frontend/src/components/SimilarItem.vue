<template>
  <div class="flex flex-center justify-center row">
    <div class="col-7">
    <q-btn 
      :href="product.url"
      target="_blank"
      class="rounded-borders my-product q-ma-sm"
      round
    >
      <q-avatar
        size="110px"
        rounded
      >
        <q-img :src="product.image" />
      </q-avatar>
    </q-btn>
    </div>
    <div class="col">
    <div class="no-wrap">
      <q-img :src="imageUrl(product.shop.image)" fit="scale-down" style="width: 30px; height: 30px;" />
      <q-chip outline color="orange" text-color="white">{{ Math.round(product.price.price).toLocaleString() }} ₴</q-chip>
    </div>
    <div class="text-caption text-grey text-center" style="width: 100px;">
      {{ product.name }}
    </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const imageUrl = (path) => { return process.env.MEDIA_URI + path }
</script>

<style lang="sass" scoped>
.my-product .text-subtitle2 
  text-transform: none
  line-height: 1.15rem
</style>