<script setup lang="ts">
import { DownOutlined } from '@ant-design/icons-vue'
import { Button, Dropdown, Menu } from 'ant-design-vue'

import { MARKET_USER_OWNER, USER_TYPES } from '@/views/Home/components/TeamMarket/config/market'

const props = defineProps({
  userType: {
    type: String,
    default: '',
  },
  popContainerType: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['change'])
function menuItemClick(menuItem) {
  menuItem.domEvent.stopPropagation()
  menuItem.domEvent.preventDefault()
  emit('change', menuItem.key)
}

const userTypes = USER_TYPES.filter(item => item.key !== MARKET_USER_OWNER)
const getPopContainer = triggerNode => (props.popContainerType === 'parent' ? triggerNode.parentNode : document.body)
const getTypeName = userType => USER_TYPES.find(item => item.key === userType)?.name
</script>

<template>
  <Dropdown
    :get-popup-container="getPopContainer"
    :disabled="userType === MARKET_USER_OWNER"
  >
    <Button style="padding: 0 5px 0 0;" type="link" class="ant-dropdown-link inline-flex items-center" @click="e => e.preventDefault()">
      <span>{{ getTypeName(props.userType) }}</span>
      <DownOutlined />
    </Button>
    <template #overlay>
      <Menu
        slot="overlay"
        style="padding: 0;"
        @click="(menuItem) => menuItemClick(menuItem)"
      >
        <Menu.Item v-for="item in userTypes" :key="item.key" class="powerItem">
          {{ item.name }}
        </Menu.Item>
      </Menu>
    </template>
  </Dropdown>
</template>

<style lang="scss" scoped>

</style>
