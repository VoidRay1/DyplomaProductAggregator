<template>
  <q-input
    v-model="value"
    outlined
    bottom-slots
    input-class="text-subtitle1"
    :error="validation.$error"
    :error-message="errorMessage()"
    :autocomplete="field.autocomplete"
    :disabled="field.disabled"
    :class="field.classes"
    :label="field.label"
    :maxlength="field.maxLength"
    :minlength="field.minLength"
    :placeholder="field.placeholder"
    :readonly="field.readonly"
    :type="field.component.params.type || 'text'"
    @blur="validation.$touch"
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

const errorMessage = () => {
  if (!(props.field.validation && props.field.validation.errors)) {
    return ''
  }
  // select error message from most specific to least specific
  const {validation: {errors}} = props.field
  for (const key in props.validation) {
    if (key.startsWith('$')) {
      // ignore special keys
      continue
    }
    if (props.validation[key]) {
      // value is valid, continue
      continue
    }
    if (key in errors) {
      return errors[key]
    }
  }
  return errors.invalid || errors.error || ''
}
</script>