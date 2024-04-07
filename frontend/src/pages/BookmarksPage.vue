<template>
  <q-page class="flex flex-center content-start">
    <q-card class="my-card">
      <q-card-section>
        <div class="text-h5">{{ __('Bookmarks') }}</div>
      </q-card-section>
      <q-separator />
      <q-card-section>
        <div v-if="products.edges?.length"
          class="q-pa-md row items-start q-gutter-lg"
        >
          <BookmarkItem v-for="product in products.edges"
            :key="product.node.id"
            :product="product.node"
          />
          <LoadingSpinner v-if="loading" />
          <div v-else class="text-center" style="width: 100%;">
            <q-btn v-if="hasNextPage"
              @click="loadMore"
              outline
              rounded
              color="primary"
              :label="__('Show more')"
            />
          </div>
          <div v-if="error">
            Error: {{ error.message }}
          </div>
        </div>
        <div v-else>
          <LoadingSpinner v-if="loading" />
          <div class="text-center q-mb-lg">
            <q-img
              src="~assets/empty_cart.webp"
              width="400px"
              fit="contain"
            />
          </div>
          <div class="text-h6 text-grey text-center q-mb-xl">
            <p>{{ __("Looks like you don't have any product preferences?") }}</p>
            <router-link to="/shops" class="link">
              {{ __('Find your favourite products') }}
            </router-link>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>
  
<script setup>
import { ref, computed } from 'vue'
import { useGettext } from 'vue3-gettext'
import LoadingSpinner from 'components/LoadingSpinner.vue'
import BookmarkItem from 'components/BookmarkItem.vue'
import { useQuery } from '@vue/apollo-composable'
import { GET_TRACK_PRODUCTS } from '../constants/graphql'

const pageSize = 20
const { current } = useGettext()
const language = localStorage.getItem('language') || current

const {
  result,
  loading,
  error,
  fetchMore
} = useQuery(GET_TRACK_PRODUCTS, {
  language: language,
  first: pageSize
})
  
function loadMore () {
  fetchMore({
    variables: {
      after: result.value?.trackProducts.pageInfo.endCursor
    }
  })
}
  
const products = computed(() => result.value?.trackProducts ?? [])
const hasNextPage = computed(() => result.value?.trackProducts.pageInfo.hasNextPage ?? false)
</script>
