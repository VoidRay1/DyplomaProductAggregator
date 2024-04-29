<template>
  <div class="q-pa-md row justify-center">
    <div class="col">
      <q-form
        @submit="$emit('search-products', query)"
        method="GET"
      >
        <q-input
          @clear="$emit('cancel-search')"
          v-model="query"
          name="q"
          :label="__('Search')"
          clearable
          clear-icon="close"
          outlined
          color="orange"
        />
      </q-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useGettext } from 'vue3-gettext'

const query = ref('')
const { current } = useGettext()
const language = localStorage.getItem('language') || current

</script>