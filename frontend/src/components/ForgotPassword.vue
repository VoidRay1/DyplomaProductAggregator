<template> 
  <q-page class="flex flex-center">
    <q-dialog v-model="forgot">
      <q-card class="forgot-card">
        <q-card-section class="row items-center">
          <div class="text-h6">
            {{ __('Forgot password?') }}
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator />
        <q-card-section class="q-gutter-y-md column">
          <q-input
            outlined
            color="orange"
            v-model="email"
            :label="__('Email')"
            :hint="__('Email hint')"
            @blur="v$.email.$touch"
            :error="v$.email.$dirty && v$.email.$invalid"
          >
            <template v-slot:prepend>
              <q-icon name="alternate_email" />
            </template>
            <template v-slot:error>
              <p v-for="error in v$.email.$errors" :key="error.$uid">{{ error.$message }}</p>
            </template>
          </q-input>
        </q-card-section>
        <q-separator />
        <q-card-actions class="justify-center">
          <q-btn
            v-close-popup
            no-caps
            color="orange"
            :label="__('Send')"
            :disabled="v$.$invalid"
            @click="forgotPassword"
            style="width: 120px;"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>>    
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { required, email } from '../utils/i18n-validators'

export default defineComponent({
  name: 'ForgotPassword',
  setup () {
    const email = ref('') 
    return {
      v$: useVuelidate(),
      forgot: ref(true),
      email,
    }
  },
  validations () {
    return {
      email: { required, email }
    }
  },
  methods: {
    forgotPassword () {

    }
  }
})
</script>

<style lang="sass" scoped>
.forgot-card
  width: 320px
  max-width: 50vw
</style>