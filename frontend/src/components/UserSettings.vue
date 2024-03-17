<template>
  <q-page class="flex flex-center content-start">
    <q-card class="my-card q-mb-lg">
      <q-card-section>
        <div class="text-h5">{{ __('Settings') }}</div>
      </q-card-section>
      <q-separator />
      <LoadingSpinner v-if="loading" />
      <div v-else-if="error">
        Error: {{ error.message }}
      </div>
      <q-card-section v-else-if="result">
        <FormGenerator
          v-model="model"
          :schema="schema"
          @submit="onSubmit"
        />
      </q-card-section>
    </q-card>
  </q-page>
</template>
    
<script setup>
import { useQuasar } from 'quasar'
import { computed, watch, reactive } from 'vue'
import { useGettext } from 'vue3-gettext'
import { useQuery, useMutation } from '@vue/apollo-composable'
import { GET_PREFERENCES, SET_PREFERENCES } from '../constants/graphql'
import LoadingSpinner from 'components/LoadingSpinner.vue'
import FormGenerator from 'components/FormGenerator.vue';

const $q = useQuasar()
const { $gettext, current } = useGettext()
const language = localStorage.getItem('language') || current

const {
  result,
  loading,
  error
} = useQuery(GET_PREFERENCES, () => ({
  language: language
}))
const preferences = computed(() => result.value?.preferences ?? [])

const model = reactive(JSON.parse(localStorage.getItem('userPreferences')) ?? {})
const schema = reactive(JSON.parse(localStorage.getItem('schemaPreferences')) ?? {})
watch(preferences, (newValue, oldValue) => {
  let key = ''
  newValue.forEach(element => {
    key = element.section + '.' + element.name
    model[key] = element.value
    schema[key] = {
      section: element.section,
      label: element.verboseName,
      inputType: element.field.inputType,
      placeholder: element.helpText,
    }
  })
  localStorage.setItem('userPreferences', JSON.stringify(model))
  localStorage.setItem('schemaPreferences', JSON.stringify(schema))
})
      // const schema = {
      //   name: {
      //     label: 'Name',
      //     inputType: 'text',
      //     range: 'string',
      //     placeholder: 'Your name',
      //     validation: {
      //       minLength: 1,
      //       required: true,
      //       errors: {
      //         invalid: 'Your name is required.'
      //       }
      //     }
      //   },
      //   happy: {
      //     label: 'Happy',
      //     inputType: 'boolean'
      //   },
      // }
const items = reactive([])
const onSubmit = () => {
  for (const key in model) {
    const field = key.split('.')
    items.push({
      section: field[0],
      name: field[1],
      value: model[key]
    })
  }
  updatePreferences()
  items.splice(0, items.length)
}

const { mutate: updatePreferences, onDone, onError } = useMutation(SET_PREFERENCES, () => ({
  variables: {
    items: items
  }
}))

onDone((response) => {
  localStorage.setItem('userPreferences', JSON.stringify(model))
  $q.notify({
    type: 'positive',
    message: $gettext('Preferences update successful')
  })
})

onError((error) => {
  console.log(error)
  $q.notify({
    type: 'negative',
    message: error
  })
})
</script>