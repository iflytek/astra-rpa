<script lang="ts" setup>
import ConfigProvider from '@/components/ConfigProvider/index.vue'
import MultiChat from '@/components/MultiChat/Index.vue'
</script>

<template>
  <ConfigProvider>
    <MultiChat />
  </ConfigProvider>
</template>

<style lang="scss">
#multi-chat {
  width: 100%;
  height: 100%;
}
</style>
