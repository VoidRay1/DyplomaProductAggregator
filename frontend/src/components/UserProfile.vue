<template>
  <q-page class="flex flex-center content-start">
    <q-card class="my-card q-mb-lg">
      <q-card-section>
        <div class="text-h5">{{ __('Profile') }}</div>
      </q-card-section>
      <q-separator />
      <q-card-section horizontal class="justify-around q-pt-md">

      <q-card-section class="text-center q-pa-none">
        <DropZone class="dropzone-avatar content-center q-pt-lg" @files-dropped="addAvatar">
          <q-btn
            round
            no-caps
            color="white"
            @mouseover="isAvatarHovered = true"
            @mouseleave="isAvatarHovered = false"
          >
            <label for="fileAvatar">
              <q-avatar size="164px" style="cursor: pointer;">
                <q-img :src="avatar" fit="scale-down">
                  <div class="absolute-full text-subtitle2 flex flex-center" v-show="isAvatarHovered">
                    {{ __('Upload a photo') }}
                  </div>
                </q-img>            
                <q-badge
                  floating
                  rounded
                  outline
                  style="border: none;"
                  v-show="!isDefault"
                >
                  <q-btn
                    round
                    color="orange"
                    size="sm"
                    icon="close"
                    @click="clearAvatar()"
                  />
                </q-badge>
              </q-avatar>
            </label>
            <q-file
              borderless
              clearable
              v-model="file"
              for="fileAvatar"
              v-show="false"
              accept=".webp,.jpg,.jpeg,.png,.gif"
              max-file-size="1000000"
            />
          </q-btn>
        </DropZone>
        <div class="flex flex-center row q-pt-md">
          <q-input
            outlined
            dense
            color="orange"
            v-model="formData.username"
            @blur="v$.username.$touch"
            :error="v$.username.$invalid"
            style="width: 390px;"
          >
            <template v-slot:before>
              <div class="text-subtitle1 label">{{ __('Username') }}</div>
            </template>
            <template v-slot:error>
              <p v-for="error in v$.username.$errors" :key="error.$uid">{{ error.$message }}</p>
            </template>
            <template v-slot:prepend>
              <q-icon name="person_outline" />
            </template>
          </q-input>
        </div>
        <div class="flex flex-center row">
          <q-input
            outlined
            dense
            color="orange"
            v-model="formData.telegramUsername"
            @blur="v$.telegramUsername.$touch"
            :error="v$.telegramUsername.$invalid"
            style="width: 390px;"
          >
            <template v-slot:before>
              <div class="text-subtitle1 label">{{ __('Telegram username') }}</div>
            </template>
            <template v-slot:error>
              <p v-for="error in v$.telegramUsername.$errors" :key="error.$uid">{{ error.$message }}</p>
            </template>
            <template v-slot:prepend>
              <i class="fa-brands fa-telegram"></i>
          </template>
          </q-input>
        </div>
      </q-card-section>

      <q-card-section class="justify-center q-pa-none">
        <!-- <q-tabs
          v-model="tab"
          dense
          narrow-indicator
          class="text-orange"
          align="justify"
        >
          <q-tab name="account" :label="__('Personal data')" />
          <q-tab name="settings" :label="__('Settings')" />
        </q-tabs>
        <q-tab-panels v-model="tab" animated>
          <q-tab-panel name="account" class="q-pb-none"> -->
        <div class="flex flex-center row">
          <q-input
            outlined
            dense
            color="orange"
            v-model="formData.firstName"
            @blur="v$.firstName.$touch"
            :error="v$.firstName.$invalid"
            style="width: 390px;"
          >
            <template v-slot:before>
              <div class="text-subtitle1 label">{{ __('Name') }}</div>
            </template>
            <template v-slot:error>
              <p v-for="error in v$.firstName.$errors" :key="error.$uid">{{ error.$message }}</p>
            </template>
          </q-input>
        </div>
        <div class="flex flex-center row">
          <q-input
            outlined
            dense
            color="orange"
            v-model="formData.lastName"
            @blur="v$.lastName.$touch"
            :error="v$.lastName.$invalid"
            style="width: 390px;"
          >
            <template v-slot:before>
              <div class="text-subtitle1 label">{{ __('Last name') }}</div>
            </template>
            <template v-slot:error>
              <p v-for="error in v$.lastName.$errors" :key="error.$uid">{{ error.$message }}</p>
            </template>
          </q-input>
        </div>
        <div class="flex flex-center row">
        <q-input
          outlined
          dense
          color="orange"
          v-model="formData.dateOfBirth"
          @blur="v$.dateOfBirth.$touch"
          :error="v$.dateOfBirth.$invalid"
        >
          <template v-slot:before>
            <div class="text-subtitle1 label">{{ __('Date of birth') }}</div>
          </template>
          <template v-slot:error>
            <p v-for="error in v$.dateOfBirth.$errors" :key="error.$uid">{{ error.$message }}</p>
          </template>
          <template v-slot:prepend>
            <q-icon name="event" class="cursor-pointer">
              <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                <q-date
                  v-model="formData.dateOfBirth"
                  mask="YYYY-MM-DD"
                  color="orange"
                >
                  <div class="row items-center justify-end">
                    <q-btn v-close-popup label="Close" color="black" flat />
                  </div>
                </q-date>
              </q-popup-proxy>
            </q-icon>
          </template>
        </q-input>
        </div>
        <div class="flex flex-center row">
          <q-input
            disable
            outlined
            dense
            color="orange"
            v-model.trim="formData.email"
            @blur="v$.email.$touch"
            :error="v$.email.$dirty && v$.email.$invalid"
          >
            <template v-slot:before>
              <span class="text-subtitle1 label">{{ __('Email') }}</span>
            </template>
            <template v-slot:error>
              <p v-for="error in v$.email.$errors" :key="error.$uid">{{ error.$message }}</p>
            </template>
            <template v-slot:prepend>
              <q-icon name="alternate_email" />
            </template>
          </q-input>
        </div>
        <div class="flex flex-center row">
        <q-input
          outlined
          dense
          color="orange"
          v-model="formData.phone"
          placeholder="(___) ___ - ____"
          mask="(###) ### - ####"
          @blur="v$.phone.$touch"
          :error="v$.phone.$dirty && v$.phone.$invalid"
        >
          <template v-slot:before>
            <span class="text-subtitle1 label">{{ __('Phone number') }}</span>
          </template>
          <template v-slot:error>
            <p v-for="error in v$.phone.$errors" :key="error.$uid">{{ error.$message }}</p>
          </template>
          <template v-slot:prepend>
            <q-icon name="phone" />
          </template>
        </q-input>
        </div>
        <div class="flex flex-center row">
          <q-select
          outlined
          dense
          v-model="formData.country"
          use-input
          hide-selected
          fill-input
          map-options
          emit-value
          input-debounce="0"
          :options="countriesOptionsRef"
          @filter="filterCountries"
          @blur="v$.country.$touch"
          :error="v$.country.$invalid"
          options-selected-class="text-orange"
          color="orange"
          style="width: 390px;"
          behavior="menu"
      >

            <template v-slot:before>
              <span class="text-subtitle1 label">{{ __('Country') }}</span>
            </template>
            <template v-slot:error>
              <p v-for="error in v$.phone.$errors" :key="error.$uid">{{ error.$message }}</p>
            </template>
            <template v-slot:prepend>
              <q-icon name="place" />
            </template>
          </q-select>
        </div>
          <!-- </q-tab-panel>
          <q-tab-panel name="settings">
            <UserSettings />
          </q-tab-panel>
        </q-tab-panels> -->
      </q-card-section>
      </q-card-section>

      <q-separator />
      <q-card-actions v-if="hasFormChanged" class="justify-center">
        <div class="q-py-sm">
          <!--q-btn
            no-caps
            outline
            :label="__('Cancel')"
            @click="history.back()"
            color="primary"
            class="my-btn"
          /-->
          <q-btn
            no-caps
            :label="__('Save')"
            @click="submitForm"
            color="orange"
            class="my-btn"
          />
        </div>
      </q-card-actions>
    </q-card>
  </q-page>
</template>
  
<script setup>
import { useQuasar } from 'quasar'
import { reactive, computed, watch, ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import { useVuelidate } from '@vuelidate/core'
import { required, email } from '../utils/i18n-validators'
import { useQuery, useMutation } from '@vue/apollo-composable'
import { GET_USER, SET_USER, UPLOAD_PHOTO } from '../constants/graphql'
//import UserSettings from 'components/UserSettings.vue'
import DropZone from 'components/DropZone.vue'
import { minLength } from '@vuelidate/validators'

//const emit = defineEmits(['update:model-value'])

const $q = useQuasar()
const gettext = useGettext()
const { $gettext } = useGettext()
const language = localStorage.getItem('language') || gettext.current

if (gettext.current != language) {
  gettext.current = language
}
//import('../language/quasar_' + language).then(lang => {
//  $q.lang.set(lang.default)
//})

function addAvatar(newFiles) {
  file.value = newFiles[0]
}

//const isPwd = ref(true)
const file = ref(null)
const isAvatarHovered = ref(false)
const defaultAvatar = '/src/assets/avatar-icon.svg'
//const tab = ref('account')

const countriesOptions = reactive([{label: 'None', value: null}])
import(/* @vite-ignore */`../i18n/${language}/country.js`).then(country => {
   for (let key in country.default) {
    countriesOptions.push({
      label: country.default[key],
      value: key
    })
   }
})
const countriesOptionsRef = ref(countriesOptions)

function filterCountries(value, update){
  update(() => {
    const needle = value.toLowerCase()
    countriesOptionsRef.value = countriesOptions.filter(v => v.label.toLowerCase().indexOf(needle) > -1)
  })
}

function isTelegramUsernameValid(telegramUsername){
  let telegramUsernamePattern = new RegExp('^[a-z0-9_]+$')
  return telegramUsernamePattern.test(telegramUsername)
}

const formData = reactive(JSON.parse(localStorage.getItem('userData')) ?? {
  avatar: '',
  firstName: '',
  lastName: '',
  dateOfBirth: '',
  username: '',
  email: '',
  phone: '',
  country: '',
  telegramUsername: '',
})
const rules = {
  avatar: { required: false },
  firstName: { required: false },
  lastName: { required: false },
  dateOfBirth: { required: false },
  username: { required: false },
  email: { required, email },
  phone: { required: false, minLength: minLength(10) },
  country: { required: false },
  telegramUsername: {required: false, minLength: minLength(5), isTelegramUsernameCorrect:{
    $validator: isTelegramUsernameValid,
    $message: "Incorrect username format"
  }},
}

let defaultFormData = ref(JSON.stringify(formData))

const hasFormChanged = computed(() => {
    return JSON.stringify(formData) !== defaultFormData.value;
});

const v$ = useVuelidate(rules, formData)

const imageUrl = (path) => { return process.env.MEDIA_URI + path }
const avatar = ref(defaultAvatar)
if (formData.avatar) {
  avatar.value = imageUrl(formData.avatar)
}
const isDefault = computed(() => avatar.value == defaultAvatar)

const clearAvatar = () => {
  formData.avatar = ''
  avatar.value = defaultAvatar
}

watch(file, (file) => {
  formData.avatar = URL.createObjectURL(file);
  avatar.value = formData.avatar
})

const submitForm = async () => {
  const result = await v$.value.$validate()
  console.log(result)
  if (result) {
    updateProfile()
    if (file.value) {
      uploadPhoto()
    }
  } else {
//    alert('error')
  }
}

const { result } = useQuery(GET_USER)
const user = computed(() => result.value?.viewer ?? [])

watch(user, (user) => {
  formData.avatar = user.profile.avatar
  formData.firstName = user.profile.firstName
  formData.lastName = user.profile.lastName
  formData.telegramUsername = user.profile.telegramUsername
  formData.dateOfBirth = user.profile.dateOfBirth
  formData.country = user.profile.country
  formData.username = user.username
  formData.email = user.email
  formData.phone = user.phone
  if (formData.avatar) {
    avatar.value = imageUrl(formData.avatar)
  }
  localStorage.setItem('userData', JSON.stringify(formData))
})

const { mutate: updateProfile, onDone, onError } = useMutation(SET_USER, () => ({
  variables: {
    user: formData
  }
}))

onDone((response) => {
  defaultFormData.value = JSON.stringify(formData)
  localStorage.setItem('userData', JSON.stringify(formData))
  $q.notify({
    type: 'positive',
    message: $gettext('Profile update successful')
  })
})

onError((error) => {
  console.log(error)
  $q.notify({
    type: 'negative',
    message: error
  })
})

const { mutate: uploadPhoto } = useMutation(UPLOAD_PHOTO, () => ({
  variables: {
    file: file.value
  },
  context: {
    hasUpload: true
  }
}))
</script>

<style lang="sass" scoped>
.dropzone-avatar
  width: 390px
  height: 224px
  display: inline-block
  border-radius: 20px
  border: 2px dashed #d9d9d9
  background-image: url("assets/dragdrop.png")
  background-size: 40px
  background-repeat: no-repeat
  background-position: 15px 10px
.dropzone-avatar[data-active=true]
  border: 2px dashed #ff9800
.label
  width: 160px
  text-align: right
.my-btn
  min-width: 120px
</style>