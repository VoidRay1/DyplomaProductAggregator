<template>
  <div v-if="products"
    class="q-pt-md row items-start q-gutter-sm"
  >
    <div class="col-12">
      <ShopCategory :shop="shop" :filters="productFilters" :key="refreshKey" @select:Category="selectCategory" />
    </div>

    <div class="col-12 row q-pt-md">
      <div class="col-8">
        <ShopProductFilter :filters="filters" @select:Filters="selectFilters" />
      </div>
      <div class="col">
        <SortSelect @update:model-value="onSelect" />
      </div>
    </div>

    <LoadingSpinner v-if="loading" />
    <q-card v-for="product in products.edges"
      :key="product.node.id"
      class="product"
      flat
    >
      <ShopProduct :product="product.node" />
    </q-card>
    <div class="text-center" style="width: 100%;">
      <q-btn v-if="hasNextPage"
        @click="loadMore"
        outline
        rounded
        color="orange"
        :label="__('Show more')"
      />
    </div>
    <div v-if="error">Error: {{ error.message }}</div>
  </div>
</template>
  
<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGettext } from 'vue3-gettext'
import LoadingSpinner from 'components/LoadingSpinner.vue'
import ShopCategory from "components/ShopCategory.vue";
import SortSelect from 'components/SortSelect.vue'
import ShopProduct from 'components/ShopProduct.vue'
import ShopProductFilter from 'components/ShopProductFilter.vue'
import { useQuery } from '@vue/apollo-composable'
import { GET_SHOP_FILTERS, GET_SHOP_PRODUCTS } from '../constants/graphql'

const props = defineProps({
  shop: {
    type: Object,
    required: true
  }
})

const pageSizeShop = 25
const router = useRouter()
const { current } = useGettext()
const language = localStorage.getItem('language') || current

const category = ref(null)
const sortBy = ref('percent')
const sortDirection = ref('desc')

const shopFilters = useQuery(GET_SHOP_FILTERS, {
  shop: props.shop.id,
  category: category,
  language: language,
})

const filters = computed(() => shopFilters.result.value?.shopFilters.filters ?? [])

const refreshKey = ref(0);
const productFilters = ref({})

const {
  result,
  loading,
  error,
  refetch,
  fetchMore
} = useQuery(GET_SHOP_PRODUCTS, {
  shop: props.shop.id,
  category: category,
  filters: productFilters,
  sortBy: sortBy,
  sortDirection: sortDirection,
  language: language,
  first: pageSizeShop,
})
  
const loadMore = () => {
  fetchMore({
    variables: {
      after: result.value?.shopProducts.pageInfo.endCursor
    }
  })
}
  
const products = computed(() => result.value?.shopProducts ?? [])
const hasNextPage = computed(() => result.value?.shopProducts.pageInfo.hasNextPage ?? false);

const onSelect = (sort) => {
  sortBy.value = sort.by
  sortDirection.value = sort.direction
  refetch({
    sortBy: sortBy.value,
    sortDirection: sortDirection.value,
  })
}

const selectCategory = (categorySlug) => {
  category.value = categorySlug
  refetch({
    category: category.value
  })
}
const selectFilters = (filters) => {
  // console.log(filters)
  refreshKey.value += 1
  productFilters.value = {
    price: {
      min: parseInt(filters.price.min),
      max: parseInt(filters.price.max)
    },
    volume: filters.volume,
    brand: filters.brand,
    promo: filters.promo,
  }
  refetch({
    filters: productFilters.value
  })
}
</script>
  
<style lang="sass" scoped>
.product
  width: 100%
  max-width: 179px
  height: 320px
</style>