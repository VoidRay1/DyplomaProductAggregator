<template>
  <q-card-section class="q-pa-none">
    <router-link :to="{ name: 'productInfo', params: { productSlug: product.productSlug } }" style="text-decoration: none;">
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
      </div>
      <div class="absolute" style="right: 0px; top: 0px;">
        <q-btn
          round
          flat
          size="md"
          :color="product.isTracked ? 'orange' : 'grey-5'"
          :icon="product.isTracked ? 'bookmark' : 'bookmark_outline'"
          @click.prevent="product.isTracked ? untrackProduct() : trackProduct()"
        />
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
    </router-link>
    <div v-show="product.promoted" class="promo">
      <img src="~assets/promoted-label.png">
    </div>
  </q-card-section>
</template>
  
<script setup>
import { RouterLink } from 'vue-router' 
import { useQuasar } from 'quasar'
import { useGettext } from 'vue3-gettext'
import { useTokenStore } from 'stores/token'
import { useMutation } from '@vue/apollo-composable'
import { TRACK_PRODUCT, UNTRACK_PRODUCT } from '../constants/graphql'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const $q = useQuasar()
const { $gettext } = useGettext()
const token = useTokenStore()
token.initialize()

const { mutate: trackProduct, onDone, onError } = useMutation(TRACK_PRODUCT, () => ({
  variables: {
    product: props.product.id
  },
  refetchQueries: [
    'getShopProducts',
  ]
}))

const { mutate: untrackProduct, onDone: onDoneDel, onError: onErrorDel } = useMutation(UNTRACK_PRODUCT, () => ({
  variables: {
    product: props.product.id
  },
  refetchQueries: [
    'getShopProducts',
  ]
}))

onDone((response) => {
  $q.notify({
    type: 'positive',
    message: $gettext('Track product successful')
  })
})

onError((error) => {
  console.log(error)
  $q.notify({
    type: 'negative',
    message: message
  })
})

onDoneDel((response) => {
  $q.notify({
    type: 'positive',
    message: $gettext('Untrack product successful')
  })
})

onErrorDel((error) => {
  console.log(error)
  $q.notify({
    type: 'negative',
    message: message
  })
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
