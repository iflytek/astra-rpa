<script lang="ts" setup>
import DropDownMenu from '@/views/Arrange/components/process/DropdownMenu.vue'

import type { IMenuItem } from '../process/DropdownMenu.vue'
import { ProcessActionEnum, useProcessMenuActions } from '../process/hooks/useProcessMenus'

const props = defineProps<{
  processItem: RPA.Flow.ProcessModule
}>()

const menus: IMenuItem[] = useProcessMenuActions({
  item: props.processItem,
  disabled: action => props.processItem.isMain && action !== ProcessActionEnum.CLOSE_ALL,
  actions: [
    ProcessActionEnum.OPEN,
    ProcessActionEnum.RENAME,
    ProcessActionEnum.COPY,
    ProcessActionEnum.SEARCH_CHILD_PROCESS,
    ProcessActionEnum.CLOSE_ALL,
    ProcessActionEnum.DELETE,
  ],
})
</script>

<template>
  <DropDownMenu :menus="menus" trigger="contextmenu">
    <div class="flex items-center gap-1">
      <rpa-icon
        v-if="processItem.resourceId"
        name="close"
        size="16"
        class="shrink-0 cursor-pointer bg-[red]"
      />
      <span class="text-ellipsis whitespace-nowrap overflow-hidden">
        {{ processItem.name }}
      </span>
    </div>
  </DropDownMenu>
</template>
