<template>
  <q-checkbox
    v-model="value"
    :disabled="field.disabled"
    :class="field.classes"
    :label="field.label"
    :readonly="field.readonly"
    true-value="true"
    false-value="false"
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