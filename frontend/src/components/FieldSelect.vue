<template>
  <q-select
    v-model="value"
    outlined
    :autocomplete="field.autocomplete"
    :disabled="field.disabled"
    :class="field.classes"
    :label="field.label"
    :placeholder="field.placeholder"
    :readonly="field.readonly"
    :options="field.options"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps(['field', 'modelValue', 'validation'])
const emit = defineEmits(['update:modelValue'])

const value = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  }
})
</script>