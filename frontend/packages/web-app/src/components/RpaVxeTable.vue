<script lang="ts" setup>
import { ref, watch } from 'vue'

import VxeGrid from '@/plugins/VxeTable'

const { height, columns, dataSource, isScrollBottom } = defineProps({
  height: {
    type: Number,
    default: 300,
  },
  columns: {
    type: Array,
    default: () => [],
  },
  dataSource: {
    type: Array,
    default: () => [],
  },
  isScrollBottom: {
    type: Boolean,
    default: false,
  },
})
const emit = defineEmits(['cellClick', 'menuClick'])
const rpaVxeGridRef = ref(null)

function onMenuClick(params) {
  emit('menuClick', params)
}

function onCellClick(params) {
  emit('cellClick', params)
}

watch(() => dataSource.length, () => {
  if (isScrollBottom) {
    const lastRow = dataSource[dataSource.length - 1]
    setTimeout(() => {
      rpaVxeGridRef.value.scrollToRow(lastRow)
    }, 100)
  }
})
</script>

<template>
  <div class="rpa-vxe-table">
    <VxeGrid
      ref="rpaVxeGridRef"
      :height="height"
      size="mini"
      :border="true"
      :show-overflow="true"
      :keep-source="true"
      :columns="columns"
      :data="dataSource"
      :scroll-y="{ enabled: true }"
      :row-config="{ isHover: true }"
      :menu-config="{
        body: {
          options: [[{ code: 'copy', name: $t('复制') }]],
        },
        visibleMethod: ({ options }) => {
          options.forEach((list) => {
            list.forEach((item) => {
              if (item.code === 'copy') {
                item.visible = true;
              }
            });
          });

          return true;
        },
      }"
      @menu-click="onMenuClick"
      @cell-click="onCellClick"
    />
  </div>
</template>
