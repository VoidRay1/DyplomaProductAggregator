<template>
  <q-page class="flex flex-center content-start">
    <q-card class="my-card error text-center">
      <div style="font-size: 30vh; color: orange;" >
        404
      </div>
      <div class="text-h2" style="opacity:.4; color: white;">
        {{ __('Page not found') }}
      </div>
      <q-btn
        class="q-my-lg"
        text-color="blue"
        unelevated
        no-caps
        to="/"
        :label="__('Go Home')"
      />
    </q-card>
  </q-page>
</template>

<script setup>
</script>

<style lang="sass" scoped>
.error
  background-image: url("assets/error-background.png")
  background-size: no-repeat
  background-position: center
</style>