<template>
  <!-- <q-page class="flex flex-center"> -->
    <q-dialog v-model="registerDialog">
      <q-card class="register-card">
        <q-card-section class="row items-center">
          <div class="text-h6">
            {{ __('Register') }}
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator />
        <q-card-section class="q-gutter-y-lg column">
          <q-input
            outlined
            color="orange"
            v-model="username"
            :label="__('Username')"
            :hint="__('')"
            @blur="v$.username.$touch"
            :error="v$.username.$invalid"
          >
            <template v-slot:prepend>
              <q-icon name="person" />
            </template>
            <template v-slot:error>
              <p v-for="error in v$.username.$errors" :key="error.$uid">{{ error.$message }}</p>
            </template>
          </q-input>

          <q-input
            outlined
            color="orange"
            v-model.trim="email"
            :label="__('Email')"
            :hint="__('')"
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

          <q-input
            outlined
            color="orange"
            v-model="password"
            :type="isPwd ? 'password' : 'text'"
            :label="__('Password')"
            :hint="__('')"
            @blur="v$.password.$touch"
            :error="v$.password.$dirty && v$.password.$invalid"
          >
            <template v-slot:prepend>
              <q-icon name="lock" />
            </template>
            <template v-slot:append>
              <q-icon
                :name="isPwd ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="isPwd = !isPwd"
              />
            </template>
            <template v-slot:error>
              <p v-for="error in v$.password.$errors" :key="error.$uid">{{ error.$message }}</p>
            </template>            
          </q-input>
        </q-card-section>
        <q-separator />
        <q-card-actions class="justify-center q-pa-md">
          <q-btn
            v-close-popup
            no-caps
            color="orange"
            :label="__('Register')"
            :disabled="v$.$invalid"
            @click="registerUser"
            style="width: 120px;"
          />
        </q-card-actions>
        <inner-loading :loading="loading"/>
      </q-card>
    </q-dialog>
  <!-- </q-page> -->
</template>

<script>
import { defineComponent, ref } from 'vue'
import { api } from 'boot/axios'
import { useVuelidate } from '@vuelidate/core'
import { required, email, minLength } from '../utils/i18n-validators'
//import { required, email, minLength } from '@vuelidate/validators'
import InnerLoading from 'components/InnerLoading.vue'

export default defineComponent({
  name: 'RegisterForm',
  components: {
    InnerLoading
  },
  setup () {
    const username = ref('')
    const email = ref('') 
    const password = ref('')
    return {
      loading: false,
      v$: useVuelidate(),
      registerDialog: ref(true),
      username,
      email, 
      password,
      isPwd: ref(true),
    }
  },
  validations () {
    return {
      username: { required: false },
      email: { required, email },
      password: { required, minLength: minLength(8) }
    }
  },
  methods: {
    registerUser () {
      this.loading = true

      const formData = {
        username: this.username,
        email: this.email,
        password: this.password
      }
  console.log(formData)
      api.post('users/', formData)
      .then((response) => {
        console.log(response)
        //this.store.setToken(response.data.auth_token)
        this.$router.push('/')
      })
      .catch((error) => {
        console.log('error')

        console.log(error)
      })
    }
  }
})
</script>

<style lang="sass" scoped>
.register-card
  width: 400px
</style>