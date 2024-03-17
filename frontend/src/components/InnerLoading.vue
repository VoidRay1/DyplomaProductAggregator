<template>
  <q-inner-loading :showing="loading">
      <q-spinner-ios
        size="75px"
        color="primary"
      />
  </q-inner-loading>
</template>

<script setup>
const props = defineProps(['loading'])
</script>