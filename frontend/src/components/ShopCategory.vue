<template>
  <LoadingSpinner v-if="loading" />
  <q-toolbar v-if="categories" class="q-pa-none q-gutter-sm">
    <q-btn v-show="currentCategory != ''"
      outline
      rounded
      no-caps
      no-wrap
      color="grey"
      icon="arrow_back"
      :label="__('Back')"
      @click="onBack"
    />
    <q-separator  v-show="currentCategory != ''" vertical />
    <div class="q-gutter-xs">
      <q-btn
        rounded
        no-caps
        no-wrap
        color="orange"
        :outline="isAll()"
        @click="onAll"
      >
        <div class="q-pr-xs">{{ __('All') }}</div>
        <div :class="{ 'text-grey': isAll() }">{{ countAllProducts }}</div> 
      </q-btn>
      <q-btn v-for="category in categories"
        :key="category.id"
        :outline="!isCategoryActive(category)"
        :disable="category.countProducts == 0"
        rounded
        no-caps
        size="md"
        color="orange"
        class="q-py-none"
        @click="onClick(category)"
      >
        <div class="q-pr-xs">{{ category.name }}</div>
        <div :class="{ 'text-grey': !isCategoryActive(category) }">{{ category.countProducts }}</div> 
      </q-btn>
    </div>
  </q-toolbar>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useGettext } from 'vue3-gettext'
import LoadingSpinner from 'components/LoadingSpinner.vue'
import { useQuery } from '@vue/apollo-composable'
import { GET_SHOP_CATEGORIES } from '../constants/graphql'

const props = defineProps({
  shop: {
    type: Object,
    required: true
  },
  filters: {
    type: Object,
    required: false
  }
})
const emit = defineEmits(['select:Category'])

const currentCategory = ref('')
const countParentProducts = ref(0)

const isAll = () => {
  if (currentCategory.value.length === 0) return false
  if (currentCategory.value.parent === undefined) return false
  return currentCategory.value.parent !== null 
}
const isCategoryActive = (category) => {
  return currentCategory.value.categorySlug == category.categorySlug
}
const onClick = (category) => {
  if (!category.parent) {
    countParentProducts.value = category.countProducts
    refetch({
      parent: category.id
    })
  }
  emit('select:Category', category.categorySlug)
  currentCategory.value = category
}
const onAll = () => {
  refetch({
    parent: currentCategory.value.parent.id
  })
  emit('select:Category', currentCategory.value.parent.categorySlug)
  currentCategory.value = currentCategory.value.parent
}
const onBack = () => {
  refetch({
    parent: currentCategory.value.parent
  })
  emit('select:Category', currentCategory.value.categorySlug)
  currentCategory.value = ''
}

const { current } = useGettext()
const language = localStorage.getItem('language') || current

const {
  result,
  loading,
  error,
  refetch
} = useQuery(GET_SHOP_CATEGORIES, {
  shop: props.shop.id,
  parent: currentCategory.value,
  filters: props.filters,
  language: language
})

const categories = computed(() => result.value?.shopCategories.filter((item) => item.countProducts) ?? [])
const countAllProducts = computed(() => {
  if (categories.value.length == 0) {
    return countParentProducts.value
  }
  return categories.value.reduce((total, item) => total + item.countProducts, 0)
})
</script>