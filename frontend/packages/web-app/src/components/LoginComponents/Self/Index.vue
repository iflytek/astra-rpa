<!-- @format -->
<script setup>
import { TabPane, Tabs } from 'ant-design-vue'
import { ref } from 'vue'

import AccountLogin from './components/AccountLogin.vue'
import MobileLogin from './components/MobileLogin.vue'
// import OfflineCode from './OffilineCode.vue'

const activeWay = ref('online')
const activityTab = ref('account')

const mobileLoginRef = ref(null)
const accountLoginRef = ref(null)

// const loginOffline = () => {
//   activeWay.value = "offline";
// };

// function loginOnline() {
//   activeWay.value = 'online'
// }

function changeTab(key) {
  switch (key) {
    case 'account':
      if (mobileLoginRef.value)
        mobileLoginRef.value.clearValidate()
      break
    case 'phone':
      if (accountLoginRef.value)
        accountLoginRef.value.clearValidate()
      break
    default:
      break
  }
}
// const emits = defineEmits(['toggleLoginType'])
// const toggleLoginThird = () => {
//   emits("toggleLoginType", 'third');
// };
</script>

<template>
  <div class="self-container box-main">
    <div class="w-full">
      <div v-if="activeWay === 'online'" class="LoginBox">
        <!-- <div class="LoginBox-offline" @click="loginOffline">{{ $t("offlineLogin") }}</div> -->
        <h5 class="LoginBox-title">
          {{ $t("app") }}
        </h5>
        <Tabs v-model="activityTab" @change="changeTab">
          <TabPane key="account" :tab="$t('account')">
            <AccountLogin ref="accountLoginRef" />
          </TabPane>
          <TabPane key="phone" :tab="$t('phoneNumber')">
            <MobileLogin ref="mobileLoginRef" />
          </TabPane>
        </Tabs>
        <div class="other-login">
          <!-- <span class="other-title">{{ $t("otherLoginWays") }}</span>
          <span class="open_platform pointer" :title="$t('openPlatform')" @click="toggleLoginThird"/> -->
        </div>
      </div>
      <!-- <OfflineCode v-if="activeWay === 'offline'" @login-on-line="loginOnline" /> -->
    </div>
  </div>
</template>

<style lang="scss">
.self-container {
  position: absolute;
  top: 50%;
  transform: translateY(-45%);
  right: 80px;
  width: 338px;
  // height: 340px;
}

.LoginBox {
  width: 100%;
  font-size: 22px;
  position: relative;

  &-title {
    text-align: left;
    font-weight: 600;
    margin-top: 10px;
    font-size: 18px;
  }

  &-offline {
    position: absolute;
    top: -48px;
    right: -6px;
    font-size: 14px;
    font-weight: 400;
    color: $color-info;
    user-select: none;
    cursor: pointer;

    &:hover {
      color: $color-primary;
    }
  }

  .ant-tabs .ant-tabs-top-content,
  .ant-tabs .ant-tabs-bottom-content {
    width: 100%;
  }

  .ant-tabs-nav-scroll {
    text-align: left;
  }

  .other {
    &-login {
      margin-top: 20px;
      text-align: center;

      .open_platform {
        width: 36px;
        height: 36px;
        cursor: pointer;
        display: inline-block;
        margin-top: 10px;
        background-image: url(@/assets/img/login/login_open_platform.png);
      }
    }

    &-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: #999;
      font-size: 12px;

      &:before,
      &:after {
        content: ' ';
        width: 100px;
        height: 1px;
        display: inline-block;
        background: #eee;
      }
    }
  }
}

.w100 {
  width: 100%;
}

.pointer {
  cursor: pointer;
}
</style>
