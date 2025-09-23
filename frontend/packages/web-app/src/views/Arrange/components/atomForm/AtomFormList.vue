<script setup lang="ts">
import { computed } from 'vue'

import AtomFormItem from './AtomFormItem.vue'

const { atomForm } = defineProps({
  atomForm: {
    type: Array<RPA.AtomDisplayItem>,
    default: () => ([]),
  },
})

const atomFormItem = computed(() => {
  return atomForm.filter(item => !item.dynamics || [undefined, true].includes(item.show))
})
</script>

<template>
  <AtomFormItem v-for="atom in atomFormItem" :key="atom.key" :atom-form-item="atom" />
</template>
