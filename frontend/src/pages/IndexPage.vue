<template>
  <q-page class="flex flex-center content-start">
    <q-card class="my-card">
      <SearchForm />
      <NewProducts />
      <TrackProducts :isShopProductUrl="false" />
    </q-card>
  </q-page>
</template>

<script setup>
import SearchForm from 'components/SearchForm.vue'
import NewProducts from 'components/NewProducts.vue'
import TrackProducts from 'components/TrackProducts.vue'
</script>