<script setup lang="ts">
import Card from '../card.vue'

import { useBrowerPlugin } from './hooks/useBrowerPlugin'
import PluginButton from './pluginButton.vue'

// 插件列表
const { pluginList, install } = useBrowerPlugin()
</script>

<template>
  <div class="space-y-3">
    <Card
      v-for="(plugin, index) in pluginList"
      :key="plugin.type"
      class="px-6 py-4"
      :title="$t(plugin.title)"
      :description="$t(plugin.description)"
    >
      <template #prefix>
        <img class="size-9" :src="plugin.icon">
      </template>
      <template #suffix>
        <PluginButton
          :item="plugin"
          :index="index"
          @click="() => install(plugin)"
        />
      </template>
    </Card>
  </div>
</template>
