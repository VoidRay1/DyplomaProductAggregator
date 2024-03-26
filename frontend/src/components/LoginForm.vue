<template>
  <q-dialog> 
    <q-card class="login-card" v-if="!registerForm">
      <q-form @submit.prevent="loginUser()">
      <q-card-section class="row items-center">
        <div class="text-h6">{{ __('Login form') }}</div>
        <q-space />
        <q-btn
          icon="close"
          flat
          round
          dense
          v-close-popup
        />
      </q-card-section>
      <q-separator />  
      <q-card-section class="q-py-sm text-center">
        <q-avatar
          size="100px"
          color="grey-4"
          text-color="white"
          icon="fa-solid fa-user"
        />
      </q-card-section>

      <q-card-section class="q-gutter-y-md column">
        <q-input
          autofocus
          outlined
          color="orange"
          v-model="formData.email"
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
          v-model="formData.password"
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

      <q-card-actions class="q-px-md">
        <q-btn
          v-close-popup
          no-caps
          color="orange"
          :label="__('Login')"
          type="submit"
          style="width: 120px;"
        />
        <q-space />
        <router-link
          class="q-my-sm text-center text-body2 text-weight-bold text-orange no-underline"
          to="forgot"
        >
          {{ __('Forgot password?') }}
        </router-link>
      </q-card-actions>

      <q-separator />

      <q-card-actions align="center">
        <q-btn
          round
          outline
          color="orange"
          icon="fa-brands fa-google"
          @click="authenticate('google-oauth2')"
        />
        <q-btn
          round
          outline
          color="orange"
          icon="fa-brands fa-facebook"
          @click="authenticate('facebook')"
        />
      </q-card-actions>

      <q-separator />

      <q-card-actions align="center">
        <q-btn
          flat
          color="orange"
          :label="__('Register')"
          @click="registerForm = true"
        />
        <!-- <router-link
          class="q-my-sm text-center text-body2 text-weight-bold text-orange no-underline"
          to="/register"
        >
          {{ __('Register') }}
        </router-link> -->
      </q-card-actions>
      </q-form>
    </q-card>
    <RegisterForm v-model="registerForm" />
  </q-dialog>
</template>

<script setup>
import { useQuasar } from 'quasar'
import { reactive, ref, onMounted } from 'vue'
//import { api } from 'boot/axios'
import { useTokenStore } from 'stores/token'
import { useVuelidate } from '@vuelidate/core'
import { required, email, minLength } from '../utils/i18n-validators'
import { useGettext } from 'vue3-gettext'
import { useMutation } from '@vue/apollo-composable'
import { TOKEN_AUTH } from '../constants/graphql'
import RegisterForm from 'components/RegisterForm.vue'

const $q = useQuasar()
const store = useTokenStore()
const { $gettext } = useGettext()

const registerForm = ref(false)

const formData = reactive({
  email: '',
  password: '',
})
const rules = {
  email: { required, email },
  password: { required }
}
const v$ = useVuelidate(rules,formData)

function triggerPositive () {
  $q.notify({
    type: 'positive',
    message: $gettext('Login successful')
  })
}

function triggerNegative (message) {
  $q.notify({
    type: 'negative',
    message: message
  })
}

const { mutate: loginUser, onDone, onError } = useMutation(TOKEN_AUTH, () => ({ variables: formData }))

onDone((response) => {
  store.setToken(response.data.tokenAuth)
  triggerPositive()
})

onError((error) => {
  console.log(error)
  triggerNegative(error.response.data.detail)
})

const isPwd = ref(true)

const authenticate = (provider) => {
  const url = 'http://localhost:8000/social-auth/'
  window.location.href = url + 'login/' + provider + '/'
 /*     const params = {
        redirect_uri: 'http://localhost:8000/social-auth/complete/' + provider + '/'
      }
      api.get('social-auth/login/' + provider + '/', { params })
      .then((response) => {
        console.log(response.data.authorization_url)
        window.location.href = response.data.authorization_url
      })
      .catch((error) => {
        console.log(error)
      })
/*     this.$auth.authenticate('google', {provider: "google-oauth2"}).then(function (response) {
        console.log("Works!")
      }).catch(function(error) {
        console.log(error)
      })*/
}
</script>

<style lang="sass" scoped>
.login-card
  width: 320px
  max-width: 50vw
.no-underline
  text-decoration: none  
</style>