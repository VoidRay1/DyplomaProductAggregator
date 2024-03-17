<template>
  <q-btn
    flat
    round
  >
    <q-icon
      :name="languageImageURL"
      class="flag"
    />
    <q-tooltip class="bg-orange text-no-wrap">{{ __('Select your language') }}</q-tooltip>
    <q-menu auto-close>
      <q-list style="min-width: 100px" class="text-orange">
        <q-item v-for="(language, key) in $language.available"
          :key="key"
          @click="changeLanguage(key)"
          clickable
          active-class="bg-orange-2"
        >
          <q-item-section avatar>
            <q-avatar
              square
              class="flag"
            >
              <img :src="'/langs/' + key + '.png'">
            </q-avatar>
          </q-item-section>
          <q-item-section>{{ language }}</q-item-section>
        </q-item>
      </q-list>
    </q-menu>
  </q-btn>
</template>

<!-- <script setup>
import { useQuasar } from 'quasar'
import { computed, watch, ref } from 'vue'
import { useGettext } from 'vue3-gettext'

const $q = useQuasar()
const { $gettext } = useGettext()

//$q.$language.current = localStorage.getItem('language') || 'en'
const locale = ref(localStorage.getItem('language') || 'en')

const languageImageURL = computed(() => 'img:/langs/' + locale.value + '.png')

watch (locale, (newValue, oldValue) => {
  let newUrl = window.location.pathname.replace('/' + oldValue, '/' + newValue)
  $gettext.current = newValue
  localStorage.setItem('language', newValue)
  // set quasar's language too!!
  import(/* @vite-ignore */`../language/quasar_${newValue}.js`).then(language => {
//  import(/* @vite-ignore */`quasar/lang/${locale}.mjs`).then(language => {
    console.log(language.default)
    $q.lang.set(language.default)
  })
  location.replace(newUrl)
})

const changeLanguage = (newLocale) => {
  locale.value = newLocale
}
</script>
 -->
<script>
import { useQuasar } from 'quasar'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'LanguageSelect',
  computed: {
    languageImageURL() {
      return 'img:/langs/' + this.$language.current + '.png'
    }
  },
  setup () {
    const $q = useQuasar()
  },
  mounted() {
    this.$language.current = localStorage.getItem('language') || 'en'
    this.$i18n.locale = this.$language.current
  },
  methods: {
    changeLanguage(locale) {
      let newUrl = window.location.pathname.replace('/' + this.$language.current, '/' + locale)
      this.$language.current = locale
      localStorage.setItem('language', locale)
      this.$i18n.locale = locale
      // set quasar's language too!!
      import(/* @vite-ignore */`../language/quasar_${locale}.js`).then(language => {
//      import(/* @vite-ignore */`quasar/lang/${locale}.mjs`).then(language => {
        this.$q.lang.set(language.default)
      })
      location.replace(newUrl)
    }
  }
})
</script>

<style scoped>
.flag {
  width: 18px;
  height: 12px;
}
</style>