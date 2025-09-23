<script lang="ts" setup>
import { computed } from 'vue'

import CvUploadBtn from '@/views/Arrange/components/cvPick/CvUploadBtn.vue'

type PickType = 'cv' | 'element'

const { pickType, disabled, groupId } = defineProps({
  pickType: {
    type: String as () => PickType,
    required: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  groupId: {
    type: String,
    required: false,
  },
})

const emits = defineEmits(['contextmenu'])

// 分组右键菜单
const contextmenus = [
  { label: '重命名', key: 'rename' },
  { label: '添加图像', key: 'cvPick' },
  { label: '上传图像', key: 'cvUpload' },
  { label: '拾取新元素', key: 'elementPick' },
  { label: '删除分组', key: 'delete' },
]

const menus = computed(() => {
  return contextmenus.filter((item) => {
    if (pickType === 'cv') {
      return !item.key.includes('element')
    }

    return !item.key.includes('cv')
  })
})

function handleMenuClick(item) {
  emits('contextmenu', item.key)
}
</script>

<template>
  <a-dropdown
    :trigger="['contextmenu']"
    :disabled="disabled"
    overlay-class-name="pick-group-contextmenu"
  >
    <div>
      <slot name="content" />
    </div>
    <template #overlay>
      <a-menu @click="handleMenuClick">
        <template v-for="item in menus" :key="item.key">
          <!-- 特殊处理上传按钮 -->
          <a-menu-item v-if="item.key === 'cvUpload'">
            <CvUploadBtn type="text" :group-id="groupId" class="cv-upload-btn" />
          </a-menu-item>
          <!-- 常规菜单项 -->
          <a-menu-item v-else :key="item.key">
            <span>{{ item.label }}</span>
          </a-menu-item>
        </template>
      </a-menu>
    </template>
  </a-dropdown>
</template>
