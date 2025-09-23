<script lang="ts" setup>
import ConfigProvider from '@/components/ConfigProvider/index.vue'
import UserForm from '@/views/Arrange/components/customDialog/components/userFormDialog.vue'
</script>

<template>
  <ConfigProvider>
    <UserForm />
  </ConfigProvider>
</template>

<style lang="scss">
#user-form {
  width: 100%;
  height: 100%;
}
</style>
