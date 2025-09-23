<script setup lang="ts">
import { useTranslation } from 'i18next-vue'
import { ref, shallowRef } from 'vue'

import ProcessVarPane from './ProcessVarPane.vue'
import VariablePanel from './VariablePanel.vue'

defineOptions({ name: 'VariableManagement' })

const { t } = useTranslation()
const sidebarWide = ref(true)
const activeTab = ref(0)
const tabs = shallowRef([{
  lable: t('globalVariables'),
  component: VariablePanel,
}, {
  lable: t('processVariables'),
  component: ProcessVarPane,
}])
</script>

<template>
  <section class="variable-management bg-[#fff] dark:bg-[#1d1d1d]" :class="sidebarWide ? 'w-[620px]' : 'w-80'">
    <div class="flex items-center mb-4">
      <div
        class="custom-tabs flex-1 bg-[#f3f3f7] dark:bg-[rgba(255,255,255,0.04)] before:bg-[#fff] dark:before:bg-[rgba(255,255,255,0.12)] flex items-center"
        :style="{ '--slider-x': activeTab === 0 ? '1%' : '99%' }"
      >
        <div
          v-for="(item, index) in tabs" :key="item.lable"
          class="tab-btn text-[rgba(0, 0, 0, 0.65)] dark:text-[rgba(255,255,255,0.65)]"
          :class="{ active: activeTab === index }" @click="activeTab = index"
        >
          {{ item.lable }}
        </div>
      </div>
      <!-- <rpa-hint-icon :name="sidebarWide ? 'sidebar-wide' : 'sidebar-narrow'" :title="sidebarWide ? '切换到窄版' : '切换到宽版'" class="ml-[12px]" enable-hover-bg width="16px" height="16px" @click="() => sidebarWide = !sidebarWide" /> -->
    </div>
    <component :is="tabs[activeTab].component" />
  </section>
</template>

<style lang="scss" scoped>
.variable-management {
  height: 100%;
  padding: 12px 16px;

  .custom-tabs {
    position: relative;
    width: 550px;
    height: 32px;
    border-radius: 8px;
    padding: 2px;
    box-sizing: border-box;
    overflow: hidden;
    display: flex;
    align-items: center;

    &::before {
      content: '';
      position: absolute;
      top: 2px;
      left: 0;
      width: 50%;
      height: 28px;
      border-radius: 6px;
      box-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.04);
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 0;
      pointer-events: none;
      transform: translateX(var(--slider-x, 0%));
    }
  }

  .tab-btn {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 12px;
    font-family:
      PingFang SC,
      PingFang SC-400;
    font-weight: 400;
    text-shadow: 0px 4px 4px 0px rgba(0, 0, 0, 0.04);
    cursor: pointer;
    z-index: 1;
    transition: color 0.2s;
    height: 100%;
    position: relative;

    &.active {
      font-family:
        PingFang SC,
        PingFang SC-500;
      font-weight: 500;
      color: rgba(0, 0, 0, 0.85);

      .dark & {
        color: rgba(255, 255, 255, 0.85);
      }
    }
  }
}
</style>
