<template>
  <q-card
    class="text-center my-spinner"
    flat
  >
    <q-spinner
      color="orange"
      size="xl"
      class="q-ma-xl"
    />
    {{ __('Loading...') }}
  </q-card>
</template>

<script setup>
</script>

<style lang="sass" scoped>
.my-spinner
  width: 100%
  background-color: transparent
</style>