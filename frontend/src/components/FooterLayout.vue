<template>
  <q-footer
    reveal
    elevated
    class="footer text-primary"
  >
    <div class="text-center q-mt-md">
      <p class="rights">
        <span>Product Aggregator</span>
        <span>&nbsp;©&nbsp;</span>
        <span class="copyright-year">{{ currentDate.getFullYear() }}</span>
        <span>&nbsp;•&nbsp;</span>
        <router-link to="/about">{{ __('About') }}</router-link>
      </p>
    </div>
    <div class="text-center">
      <p>
        <a href="https://t.me/product_aggregator_bot" target="_blank">
          <q-img width="20px" height="20px" src="~/assets/telegram.svg" class="" alt="Telegram Bot" />
        </a>
      </p>
    </div>
  </q-footer>
</template>

<script setup>
const currentDate = new Date()
</script>

<style lang="sass" scoped>
.footer
  background-color: $blue-grey-10
.rights
  color: $blue-grey-11
  font-size: 13px
a
  color: $amber-9
  --color: #fba505
  text-decoration: none
  transition: 250ms
a:hover, a:focus
  color: $amber-8
  --color: #ffcb6a
  text-decoration: none
  outline: none
</style>