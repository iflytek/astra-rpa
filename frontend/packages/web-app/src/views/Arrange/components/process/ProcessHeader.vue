<script setup lang="ts">
import { computed, nextTick, reactive, useTemplateRef, watch } from 'vue'
import draggable from 'vuedraggable'

import { useProcessStore } from '@/stores/useProcessStore'

import ProcessHeaderAdd from './ProcessHeaderAdd.vue'
import ProcessHeaderMore from './ProcessHeaderMore.vue'
import ProcessItem from './ProcessItem.vue'

const processStore = useProcessStore()
const processOpenBox = useTemplateRef<HTMLDivElement>('processOpenBox')

const openProcessList = computed(() => {
  const list = processStore.processList.filter(item => item.isOpen)
  return list.map((item, index) => {
    return {
      ...item,
      showDivider: ![item.resourceId, list[index + 1]?.resourceId].includes(processStore.activeProcessId),
    }
  })
})

const visibleStateMap = reactive<Record<RPA.Flow.ProcessModule['resourceId'], boolean>>({})
const inVisibleProcessList = computed(() => openProcessList.value.filter(item => visibleStateMap[item.resourceId] !== true))

function updateVisibleState(process: RPA.Flow.ProcessModule, visible: boolean) {
  visibleStateMap[process.resourceId] = visible
}

watch(() => processStore.activeProcessId, (val) => {
  nextTick(() => {
    const activeProcessDom = document.getElementById(`process_${val}`)
    activeProcessDom?.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'nearest',
    })
  })
})
</script>

<template>
  <div class="process right-tab-close-area">
    <div id="drag" ref="processOpenBox" class="process_list">
      <draggable
        item-key="resourceId"
        :list="openProcessList"
        filter=".forbid"
        class="whitespace-nowrap"
      >
        <template #item="{ element }">
          <ProcessItem
            :id="`process_${element.resourceId}`"
            :key="`contextmenu${element.resourceId}`"
            :process-item="element"
            :is-active="processStore.activeProcessId === element.resourceId"
            @visible-change="(visible) => updateVisibleState(element, visible)"
          />
        </template>
      </draggable>
    </div>
    <div class="process_action">
      <ProcessHeaderMore v-if="inVisibleProcessList.length" :in-visible-process-list="inVisibleProcessList" />
      <ProcessHeaderAdd />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.process {
  display: flex;
  align-items: center;

  &_list {
    /* 设置超出滚动 */
    overflow-x: auto;
    &::-webkit-scrollbar {
      display: none;
    }
  }

  &_action {
    display: flex;
    align-items: center;
    gap: 2px;
    padding: 4px;
  }
}
</style>
