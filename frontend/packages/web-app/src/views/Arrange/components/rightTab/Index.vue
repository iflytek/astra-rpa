<script setup lang="ts">
import { onClickOutside } from '@vueuse/core'
import { message } from 'ant-design-vue'
import { storeToRefs } from 'pinia'
import { ref, useTemplateRef } from 'vue'

import BUS from '@/utils/eventBus'

import PythonPackageManagement from '@/components/PythonPackageManagement/Index.vue'
import { useAppConfigStore } from '@/stores/useAppConfig'
import { useFlowStore } from '@/stores/useFlowStore'
import AtomForm from '@/views/Arrange/components/atomForm/AtomForm.vue'
import ProcessManage from '@/views/Arrange/components/process/ProcessManage.vue'
import CustomTabItem from '@/views/Arrange/components/rightTab/CustomTabItem.vue'
import CustomTabs from '@/views/Arrange/components/rightTab/CustomTabs.vue'
import VariableManage from '@/views/Arrange/components/variableManage/Index.vue'

const { colorTheme } = storeToRefs(useAppConfigStore())
const flowStore = useFlowStore()
const activeTab = ref('')
const tabsRef = useTemplateRef('tabsRef')

onClickOutside(tabsRef, (e) => {
  // 点击 "顶部工具栏/底部tab栏/流程切换栏/原子能力编辑页" 空白处关闭右侧tab
  const closeList = ['right-tab-close-area', 'ant-tabs-nav-wrap', 'virtual-scroll__wrapper']
  const target = e.target as HTMLElement
  const close = closeList.some(item => target.classList.contains(item)) && !!target.closest('.right-tab-close-area')
  if (close) {
    activeTab.value = ''
  }
})

BUS.$on('toggleAtomForm', (visible: boolean) => {
  if (!visible && activeTab.value === 'node') {
    activeTab.value = ''
  }
  else {
    activeTab.value = 'node'
  }
})

function beforeSelectChange(tab) {
  if (tab === 'node' && !flowStore.activeAtom) {
    message.warning('请选择一个原子能力')
    return false
  }
}
</script>

<template>
  <CustomTabs ref="tabsRef" v-model="activeTab" position="right" :before-select-change="beforeSelectChange" class="custom-tabs dark:text-[rgba(255,255,255,0.65)]]" :class="[colorTheme]" double-click-clear>
    <CustomTabItem name="节点参数" value="node" size="320">
      <AtomForm />
    </CustomTabItem>
    <CustomTabItem name="流程管理" value="process" size="320">
      <ProcessManage />
    </CustomTabItem>
    <CustomTabItem name="变量管理" value="variable" size="620">
      <VariableManage />
    </CustomTabItem>
    <CustomTabItem name="Python包管理" value="python" size="620">
      <PythonPackageManagement />
    </CustomTabItem>
  </CustomTabs>
</template>

<style lang="scss" scoped>
.custom-tabs {
  --tab-padding-main: 0px;
  --tab-padding-cross: 10px;
  --text-color: rgba(0, 0, 0, 0.65);
  --active-text-color: rgba(0, 0, 0, 0.85);
  --divider-color: #ecedf4;
  --tab-bar-gap: 24px;

  width: 38px;
  overflow: visible;
  z-index: 1;

  :deep(.tabs-header) {
    padding-top: 20px;
    border-left: 2px solid #ecedf4;
    border-radius: 0 6px 6px 0;
    background-color: #ffffff;

    .tab-bar {
      width: 36px;
    }
  }

  :deep(.custom-tab-panel) {
    box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
    border-radius: 6px 0 0 6px;
    overflow: hidden;
  }
}

.dark.custom-tabs {
  --text-color: rgba(255, 255, 255, 0.65);
  --active-text-color: rgba(255, 255, 255, 0.85);
  --divider-color: #141414;

  :deep(.tabs-header) {
    background-color: rgba(#ffffff, 0.04);
    border-left: 2px solid #141414;
  }

  :deep(.custom-tab-panel) {
  }
}
</style>
