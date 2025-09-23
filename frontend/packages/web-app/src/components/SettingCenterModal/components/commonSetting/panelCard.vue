<script setup lang="ts">
import { Switch } from 'ant-design-vue'
import { computed } from 'vue'

import Card from '../card.vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  value: {
    type: Boolean,
    required: true,
  },
})

const $emit = defineEmits(['input'])

const checked = computed(() => props.value)

function onChange(value: boolean) {
  $emit('input', value)
}
</script>

<template>
  <Card class="px-5 py-4" :title="props.title" :description="$t(props.description)">
    <template #suffix>
      <Switch
        v-model:checked="checked"
        @change="onChange"
      />
    </template>
  </Card>
</template>
