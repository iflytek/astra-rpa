<script setup lang="ts">
import { computed } from 'vue'

import { useProcessStore } from '@/stores/useProcessStore'

import type { IMenuItem } from './DropdownMenu.vue'
import DropDownMenu from './DropdownMenu.vue'

interface ProcessMenuItem extends IMenuItem {
  isMain: boolean
}

const props = defineProps<{
  inVisibleProcessList: RPA.Flow.ProcessModule[]
}>()

const processStore = useProcessStore()
const menus = computed(() => props.inVisibleProcessList.map(process => ({
  key: process.resourceId,
  name: process.name,
  isMain: process.isMain,
  fn: () => {
    // 假如点击项就是激活项，activeProcessId不会改变，ProcessHeader组件中的watch不会生效，需要手动触发滚动
    if (process.resourceId === processStore.activeProcessId) {
      const activeProcessDom = document.getElementById(`process_${processStore.activeProcessId}`)
      activeProcessDom?.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'nearest',
      })
    }
    else {
      processStore.saveProject().then(() => {
        processStore.openProcess(process.resourceId)
      })
    }
  },
})))

function closeProcess(item: IMenuItem) {
  processStore.saveProject().then(() => {
    processStore.closeProcess(item.key)
  })
}
</script>

<template>
  <DropDownMenu
    :menus="menus"
    trigger="click"
  >
    <rpa-hint-icon
      name="ellipsis"
      class="hover:!bg-[#D7D7FF]/[.4] dark:hover:!bg-[#5D59FF]/[.35]"
      enable-hover-bg
    />
    <template #menu-item="{ item }">
      <div class="flex items-center justify-between gap-2 max-w-[192px]">
        <span class="text-ellipsis whitespace-nowrap overflow-hidden">{{ item.name }}</span>
        <rpa-hint-icon v-if="!(item as ProcessMenuItem).isMain" name="close" size="14" @click.stop="closeProcess(item)" />
      </div>
    </template>
  </DropDownMenu>
</template>
