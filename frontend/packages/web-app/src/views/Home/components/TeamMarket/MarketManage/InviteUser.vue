<script setup lang="ts">
import { /* TODO 暂时注释掉， 后续组织架构功能完善再打开 Button, */ Select, TreeSelect } from 'ant-design-vue'
import { ref } from 'vue'

import { useCompanyInvite, usePhoneInvite } from '@/views/Home/components/TeamMarket/hooks/MarketManage/useInviteUser'
import RoleDropdown from '@/views/Home/components/TeamMarket/MarketManage/RoleDropdown.vue'

const { marketId } = defineProps({
  marketId: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['change'])

const { phoneInviteArr, userList, clearUserList, userListByPhone, selectData, keyDownChange, changePhoneUserType /* TODO 暂时注释掉， 后续组织架构功能完善再打开resetPhoneInviteArr */ } = usePhoneInvite(marketId, 'invite', emit)

const { companyInviteArr, companyTreeData, changeCompanyUserType, changeCompanySelect /* TODO 暂时注释掉， 后续组织架构功能完善再打开resetCompanyInviteArr */ } = useCompanyInvite(marketId, emit)

const inviteType = ref('phone')
// function changeInviteType() {
//   inviteType.value = inviteType.value === 'phone' ? 'org' : 'phone'
//   resetPhoneInviteArr()
//   resetCompanyInviteArr()
// }
</script>

<template>
  <div class="modal-form">
    <!-- TODO 暂时注释掉， 后续组织架构功能完善再打开 -->
    <!-- <Button type="link" style="margin: 5px 0; padding: 0;" @click="changeInviteType">
      切换到{{ inviteType === 'phone' ? "组织架构" : "手机号" }}搜索
    </Button> -->
    <Select
      v-if="inviteType === 'phone'"
      v-model:value="phoneInviteArr"
      popup-class-name="invite"
      placeholder="通过手机号邀请，可勾选确认添加多个"
      style="width: 100%"
      :get-popup-container="(triggerNode) => triggerNode.parentNode"
      show-search
      :show-arrow="false"
      mode="multiple"
      :default-active-first-option="false"
      :filter-option="false"
      option-label-prop="label"
      @search="userListByPhone"
      @change="selectData"
      @blur="clearUserList"
      @input-keydown="keyDownChange"
    >
      <Select.Option v-for="item in userList" :key="item.creatorId" :value="item.creatorId" :label="item.realName">
        <div class="option-item">
          <div class="option-item-value">
            {{ item.realName }}
          </div>
          <div class="option-item-value">
            {{ item.phone }}
          </div>
          <RoleDropdown pop-container-type="parent" :user-type="item.userType" @change="(userType) => changePhoneUserType(item, userType)" />
        </div>
      </Select.Option>
    </Select>

    <TreeSelect
      v-else
      v-model:value="companyInviteArr"
      style="width: 100%;"
      :get-popup-container="(triggerNode) => triggerNode.parentNode"
      placeholder="通过组织架构搜索，可勾选确认添加多个"
      tree-checkable
      show-search
      tree-node-filter-prop="name"
      tree-node-label-prop="name"
      :tree-data="companyTreeData"
      :field-names="{ children: 'children', label: 'name', value: 'deptOrUserId' }"
      @change="changeCompanySelect"
    >
      <template #title="item">
        <span v-if="item.type === 'dept'"> {{ item.name }}</span>
        <span v-else class="userNode">
          <span class="name">{{ item.name }}  {{ item.phone }}</span>
          <span><RoleDropdown pop-container-type="parent" :user-type="item.userType" @change="(userType) => changeCompanyUserType(item, userType)" /></span>
        </span>
      </template>
    </TreeSelect>
  </div>
</template>

<style lang="scss" scoped>
.option-item {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 300px;
  &-value {
    width: 110px;
    margin-right: 10px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
:deep(.ant-select-dropdown) {
  min-height: 200px;
}
:deep(.ant-select-dropdown .ant-select-item) {
  position: initial;
}
:deep(.ant-select-item-option) {
  align-items: center;
}
:deep(.ant-select-item-option .ant-select-item-option-state) {
  font-weight: bold;
}
:deep(ant-select-dropdown-menu-item) {
  overflow: visible;
}
</style>
