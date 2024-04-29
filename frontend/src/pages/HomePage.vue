<template>
  <q-page class="flex flex-center content-start">
    <q-card class="my-card">
      <SearchForm @search-products="submit" @cancel-search="cancel" />
      <div v-if="searchQuery !== ''"
        class="q-pt-md row items-start q-gutter-sm"
      >
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
        @click="loadMore()"
        outline
        rounded
        color="orange"
        :label="__('Show more')"
      />
    </div>
    <div v-if="error">Error: {{ error.message }}</div>
</div>
    <div v-else>
      <NewProducts />
      <TrackProducts :isShopProductUrl="false" />
    </div>
    </q-card>
  </q-page>
</template>

<script setup>
import SearchForm from 'components/SearchForm.vue'
import NewProducts from 'components/NewProducts.vue'
import TrackProducts from 'components/TrackProducts.vue'
import LoadingSpinner from 'components/LoadingSpinner.vue'
import ShopProduct from 'components/ShopProduct.vue'
import { SEARCH_PRODUCTS } from '../constants/graphql'
import { useQuery } from '@vue/apollo-composable'
import { ref, computed } from 'vue'

const searchQuery = ref('')
const productsOnPage = 25
const {
    result,
    loading,
    error,
    refetch,
    fetchMore
} = useQuery(SEARCH_PRODUCTS, () => ({ enabled: false, query: searchQuery.value, first: productsOnPage, }))
const products = computed(() => result.value?.searchProducts ?? [])
const hasNextPage = computed(() => result.value?.searchProducts.pageInfo.hasNextPage ?? false);

const loadMore = () => {
  fetchMore({
    variables: {
      after: result.value?.searchProducts.pageInfo.endCursor
    }
  })
}

function cancel(){
  searchQuery.value = ''
}

function submit(query){
  searchQuery.value = query
  refetch({
    query: searchQuery
  })
}

</script>
<style lang="sass" scoped>
.product
  width: 100%
  max-width: 179px
  height: 320px
</style>