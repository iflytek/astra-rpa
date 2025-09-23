<script setup lang="ts">
import { Slider } from 'ant-design-vue'
import { ref } from 'vue'

import { MATCH_DEGREE } from '@/views/Arrange/config/atom'

const { renderData } = defineProps({
  renderData: {
    type: Object as () => RPA.AtomDisplayItem,
    default: () => ({}),
  },
})
const emits = defineEmits(['refresh'])

const percent = ref(renderData.value as number * 100 || 95)
function change(value: number) {
  renderData.value = value / 100
  emits('refresh')
}

!renderData.value && (renderData.value = 0.95)
</script>

<template>
  <section class="atom-slider">
    <Slider v-model:value="(percent as number)" :track-style="{ backgroundColor: '#4e68f6' }" :marks="MATCH_DEGREE" @change="change">
      <template #mark="{ label, point }">
        <template v-if="point === 100">
          <strong>{{ label }}</strong>
        </template>
        <template v-else>
          {{ label }}
        </template>
      </template>
    </Slider>
    <a-input-number v-model:value="(percent as number)" class="atom-slider-number" :min="0" :max="100" :step="1" @change="change" />
  </section>
</template>

<style lang="scss" scoped>
.atom-slider {
  margin-left: 10px;
  display: flex;
  &-number {
    width: 60px;
    margin-left: 32px;
    height: 32px;
  }
  :deep(.ant-input-number-input) {
    padding: 8px;
  }
  :deep(.ant-slider) {
    width: 220px;
  }
  :deep(.ant-slider-mark-text) {
    font-size: 12px;
  }
  :deep(.ant-slider-mark-text:nth-child(2)) {
    transform: translateX(-75%) !important;
  }
  :deep(.ant-slider-mark-text:last-child) {
    transform: translateX(15%) !important;
  }
  :deep(.ant-slider-rail) {
    width: 104% !important;
  }
}
</style>
