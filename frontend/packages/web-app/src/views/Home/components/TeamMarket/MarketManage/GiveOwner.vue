<script setup lang="ts">
import { Select } from 'ant-design-vue'
import { ref } from 'vue'

import { usePhoneInvite } from '@/views/Home/components/TeamMarket/hooks/MarketManage/useInviteUser'

const props = defineProps({
  marketId: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['change'])

const { userList, userListByPhone } = usePhoneInvite(props.marketId, 'leave', emit)
const newOwner = ref('')

function changeGiveOwner(val) {
  newOwner.value = val
  emit('change', newOwner.value)
}
</script>

<template>
  <div class="modal-form">
    <div class="modal-form-title">
      你将离开团队，请选择新的团队所有者
    </div>
    <Select
      placeholder="请选择新的团队所有者"
      style="width: 100%"
      :get-popup-container="(triggerNode) => triggerNode.parentNode"
      show-search
      :show-arrow="false"
      :value="newOwner"
      :default-active-first-option="false"
      :filter-option="false"
      option-label-prop="label"
      @search="userListByPhone"
      @change="changeGiveOwner"
    >
      <Select.Option v-for="item in userList" :key="item.creatorId" :value="item.phone" :label="item.realName">
        <div class="option-item">
          <div class="option-item-value">
            {{ item.realName }}
          </div>
          <div class="option-item-value">
            {{ item.phone }}
          </div>
        </div>
      </Select.Option>
    </Select>
  </div>
</template>

<style lang="scss" scoped>
.option-item {
  display: flex;
  justify-content: center;
  align-items: center;

  &-value {
    width: 110px;
    margin-right: 10px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
