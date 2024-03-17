<template>
  <div class="row items-center no-wrap q-gutter-xs">
    <q-btn
      outline
      rounded
      no-caps
      icon="tune"
      color="orange"
      @click="dialog = true"
    >
      <div class="q-pl-sm text-grey">{{ __('Filters') }}</div>
    </q-btn>
    <q-avatar size="sm" color="orange" text-color="white">{{ countFilters }}</q-avatar>
  </div>
  
  <q-dialog v-model="dialog" position="left">
    <q-card style="width: 350px">
      <q-card-section class="q-pa-sm">
        <div class="row justify-between items-center">
          <div class="text-h6">
            {{ __('Filters') }}
          </div>
          <q-btn
            flat
            round
            size="sm"
            icon="close"
            color="grey"
            @click="dialog = false"
          />
        </div>
      </q-card-section>
      <q-separator />

      <q-card-section class="row items-center no-wrap q-pa-none">
        <q-list style="width: 100%;">
          <q-expansion-item default-opened>
            <template v-slot:header>
              <q-item-section class="text-subtitle1 q-pa-none">
                {{ __('Price') }}
              </q-item-section>
            </template>
            <q-card class="q-px-sm">
              <q-card-section>
                <div class="row items-center no-wrap q-gutter-md">
                  <q-input
                    outlined
                    dense
                    color="orange"
                    v-model="price.min"
                  >
                    <template v-slot:append>₴</template>
                  </q-input>
                  <span>&mdash;</span>
                  <q-input
                    outlined
                    dense
                    color="orange"
                    v-model="price.max"
                  >
                    <template v-slot:append>₴</template>
                  </q-input>
                </div>
                <q-range
                  v-model="price"
                  :min="priceMin"
                  :max="priceMax"
                  label
                  drag-range
                  switch-label-side
                  color="orange"
                />
              </q-card-section>
            </q-card>
          </q-expansion-item>

          <q-separator />

          <q-expansion-item :default-opened="selectVolumes.length > 0">
            <template v-slot:header>
              <q-item-section class="text-subtitle1 q-pa-none">
                {{ __('Volume') }}
              </q-item-section>
            </template>
            <q-card class="q-px-sm">
              <q-card-section class="row justify-center">
                <div v-for="filter, index in volume"
                  :key="filter.value"
                  class="col-6"
                >
                  <div v-if="allVolume || index < 10" class="flex items-center">
                    <q-checkbox
                      keep-color
                      v-model="selectVolumes"
                      :val="filter.value"
                      :label="filter.value"
                      color="orange"
                    />
                    <q-space />
                    <div class="q-pr-md text-caption text-grey">({{ filter.count }})</div>
                    <q-separator v-if="!(index % 2)" vertical />
                  </div>
                </div>
                <div class="col-6" v-if="volume.length % 2" />
                <q-btn
                  flat
                  round
                  color="orange"
                  size="sm"
                  :icon="allVolume ? 'expand_less' : 'expand_more'"
                  @click="allVolume = !allVolume"
                />
              </q-card-section>
            </q-card>
          </q-expansion-item>

          <q-separator />

          <q-expansion-item :default-opened="selectBrands.length > 0">
            <template v-slot:header>
              <q-item-section class="text-subtitle1 q-pa-none">
                {{ __('Brands') }}
              </q-item-section>
            </template>
            <q-card class="q-px-sm">
              <q-card-section class="row justify-center">
                <div v-for="filter, index in brand"
                  :key="filter.value"
                  class="col-12"
                >
                  <div v-if="allBrand || index < 5" class="flex items-center">
                    <q-checkbox
                      keep-color
                      v-model="selectBrands"
                      :val="filter.value"
                      :label="filter.value"
                      color="orange"
                    />
                    <q-space />
                    <div class="q-pr-md text-caption text-grey">({{ filter.count }})</div>
                  </div>
                </div>
                <q-btn
                  flat
                  round
                  color="orange"
                  size="sm"
                  :icon="allBrand ? 'expand_less' : 'expand_more'"
                  @click="allBrand = !allBrand"
                />
              </q-card-section>
            </q-card>
          </q-expansion-item>

          <q-separator />

          <q-expansion-item :default-opened="selectPromos.length > 0">
            <template v-slot:header>
              <q-item-section class="text-subtitle1 q-pa-none">
                {{ __('Promotions') }}
              </q-item-section>
            </template>
            <q-card class="q-px-sm">
              <q-card-section class="row">
                <div v-for="filter in promo"
                  :key="filter.value"
                  class="col-12"
                >
                  <div v-if="filter.count" class="flex items-center">
                    <q-checkbox
                      keep-color
                      v-model="selectPromos"
                      :val="filter.value"
                      :label="filter.value"
                      color="orange"
                    />
                    <q-space />
                    <div class="q-pr-md text-caption text-grey">({{ filter.count }})</div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </q-expansion-item>
        </q-list>
      </q-card-section>

      <q-separator />

      <q-card-actions class="justify-center">
        <q-btn
          outline
          color="orange"
          @click="onSubmit"
        >
          {{ __('Submit') }}
        </q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, watchEffect } from 'vue'

const props = defineProps({
  filters: {
    type: Object,
    required: true
  }
})
const emit = defineEmits(['select:Filters'])

const allVolume = ref(false)
const allBrand = ref(false)

const dialog = ref(false)
const price = ref({})
let priceMin = 0
let priceMax = 0
const volume = ref({})
const brand = ref({})
const promo = ref({})
const selectVolumes = ref([])
const selectBrands = ref([])
const selectPromos = ref([])

watchEffect(() => {
  if (props.filters) {
    for (const key in props.filters) {
      const filter = props.filters[key] || {}
      if (filter.param == 'price') {
        priceMin = filter.min
        priceMax = filter.max
        price.value = {
          min: priceMin,
          max: priceMax,
        }
      }
      if (filter.param == 'volume') {
        volume.value = filter.values
      }
      if (filter.param == 'brand') {
        brand.value = filter.values
      }
      if (filter.param == 'promo') {
        promo.value = filter.values
      }
    }
  }
})

const selectFilters = ref({})
const countFilters = ref(0)

const onSubmit = () => {
  selectFilters.value = {
    price: price.value
  }
  if (selectVolumes.value.length) {
    selectFilters.value.volume = selectVolumes.value
  }
  if (selectBrands.value.length) {
    selectFilters.value.brand = selectBrands.value
  }
  if (selectPromos.value.length) {
    selectFilters.value.promo = selectPromos.value
  }
  emit('select:Filters', selectFilters.value)
  dialog.value = false
  countFilters.value = Object.keys(selectFilters.value).length
}
</script>

<style scoped>
</style>
