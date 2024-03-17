<template>
  <div class="form-generator q-mb-lg">
    <q-form @submit.prevent="onSubmit">
      <div v-for="field in fields"
        :key="field.id"
        class="q-my-lg"
      >
        <component
          :is="field.component.name"
          v-model="value[field.id]"
          color="orange"
          :field="field"
          :validation="{}"
        />
      </div>
      <div class="flex justify-center">
        <q-btn
          no-caps
          :label="__('Save')"
          type="submit"
          color="orange"
          class="my-btn"
        />
      </div>
    </q-form>
  </div>
</template>
      
<script setup>
import { computed } from 'vue'
import FieldCheckbox from './FieldCheckbox.vue';
import FieldInput from './FieldInput.vue';
import FieldSelect from './FieldSelect.vue';

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
    default: () => ({})
  },
  schema: {
    type: Object,
    required: true,
    default: () => ({})
  },
  inputTypeMap: {
    type: Object,
    required: false,
    default: () => ({
      checkbox: 'FieldCheckbox',
      text: 'FieldInput',
      enum: 'FieldSelect'
    })
  }
})
const emit = defineEmits(['update:modelValue', 'submit'])

const fields = computed(() => {
  const fields = []
  for (const key in props.schema) {
    const s = props.schema[key] || {}
    const field = {id: key, ...s}
    const inputTypeMap = props.inputTypeMap
    field.component = _getComponent({inputTypeMap, field})
    const lookup = {
      FieldCheckbox,
      FieldInput,
      FieldSelect,
    }
    field.component.name = lookup[field.component.name]
    fields.push(field)
  }
  return fields
})

const value = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  }
})

const onSubmit = (evt) => { emit('submit', evt) }

function _getComponent({inputTypeMap, field}) {
  let component
  if (field.component) {
    component = field.component
  } else {
    let {inputType} = field
    if (!inputType) {
      switch (field.range) {
        // TODO: add other defaults
        default:
          inputType = 'text'
      }
    }
    component = inputTypeMap[inputType]
  }
  if (typeof component !== 'string') {
    return component
  }
  return {name: component, params: {}}
}
</script>

<style lang="sass" scoped>
.form-generator
  width: 100%
.my-btn
  min-width: 120px
</style>