<template>
  <q-card-section class="q-pa-none">
    <a
      :href="product.url"
      target="_blank"
      style="text-decoration: none"
    >
      <q-img
        :src="product.image"
        fit="scale-down"
        img-class="q-pa-sm"
        class="product-image"
      />
      <div class="absolute" v-show="!product.promoted">
        <div v-for="promo in product.price.promotions.edges"
          :key="promo.node.id"
          class="q-pb-xs"
        >
          <q-img 
            :src="promo.node.iconUrl"
            :title="promo.node.title"
            fit="contain"
            width="30px"
            height="30px"
            style="top: -170px; right: -5px"
          />
        </div>
            <!-- <q-btn
              round
              color="orange-4"
              icon="o_shopping_bag"
              class="q-ma-md"
              style="top: -190px; right: -75px"
              @click="addCart(item.node)"
            /> -->
      </div>
      <div class="text-body1 text-center text-weight-bold text-grey-8 q-mt-sm">
        {{ product.price.price }} ₴
      </div>
      <div class="text-body2 text-center text-grey text-strike" v-if="product.price.percent > 0">
        {{ product.price.oldPrice }} ₴
        <q-chip square dense color="orange" text-color="white">
          -{{ Math.round(product.price.percent) }}%
        </q-chip>
      </div>
      <div class="text-body2 text-grey-10 text-center">
        {{ product.name }}
      </div>
      <div class="text-body2 text-grey text-center">
        {{ product.volume }}
      </div>
    </a>
    <div v-show="product.promoted" class="promo">
      <img src="~assets/promoted-label.png">
    </div>
  </q-card-section>
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
.product-image
  width: 180px
  height: 180px
  min-width: 20px
  min-height: 20px
  background-color: white
.promo
  position: absolute
  top: 0px
  left: 0px
.title
  white-space: nowrap
  overflow: hidden
  text-overflow: ellipsis
  width: 140px
  padding: 0 5px
</style>
