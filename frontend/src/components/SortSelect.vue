<template>
  <q-select
    rounded
    outlined
    dense
    bottom-slots
    v-model="model"
    :options="options"
    color="orange"
    @update:model-value="onSelect"
  >
    <template v-slot:append>
      <q-icon name="sort" color="orange" />
    </template>
    <template v-slot:selected>
      <div class="text-grey">{{ model.label }}</div>
    </template>
  </q-select>
</template>

<script setup>
import { ref } from 'vue'
import { useGettext } from 'vue3-gettext'

const props = defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue'])

const onSelect = (value) => {
  emit('update:modelValue', value)
}

const { $gettext } = useGettext()

const options = [
  {
    label: $gettext('Max discount'),
    value: 'percent_desc',
    description: 'Сначала максимальный процент скидки',
    by: 'percent',
    direction: 'desc'
  },
  {
    label: $gettext('Min discount'),
    value: 'percent_asc',
    description: 'Сначала минимальный процент скидки',
    by: 'percent',
    direction: 'asc'
  },
  {
    label: $gettext('Min price'),
    value: 'price_asc',
    description: 'Сначала минимальная цена',
    by: 'price',
    direction: 'asc'
  },
  {
    label: $gettext('Max price'),
    value: 'price_desc',
    description: 'Сначала максимальная цена',
    by: 'price',
    direction: 'desc'
  },
  {
    label: $gettext('A - Z'),
    value: 'name_asc',
    description: 'По названию',
    by: 'name',
    direction: 'asc'
  },
  {
    label: $gettext('Z - A'),
    value: 'name_desc',
    description: 'По названию',
    by: 'name',
    direction: 'desc'
  },
]
const model = ref(options[0])

</script>

<style scoped>
</style>
