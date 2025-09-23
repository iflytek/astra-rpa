<script setup lang="ts">
import { Progress } from 'ant-design-vue'
import { watch } from 'vue'

import { useAppFileDownload } from '@/views/Home/components/TeamMarket/hooks/useAppFileDownload'
import { AppFileStatus } from '@/views/Home/types/market'

const { fileList } = defineProps({
  fileList: {
    type: Array,
    default: () => [],
  },
})
const { files, setFiles, download, cancelDownload } = useAppFileDownload()

watch(() => fileList, (newVal) => {
  setFiles(newVal)
})

function getStatus(status: AppFileStatus) {
  switch (status) {
    case AppFileStatus.downloading:
      return 'active'
    case AppFileStatus.success:
      return 'success'
    case AppFileStatus.exception:
      return 'exception'
    default:
      return 'normal'
  }
}
</script>

<template>
  <template v-if="files.length > 0">
    <div v-for="(item, index) in files" :key="index" class="file flex items-center">
      <a-button type="link" @click="download(item)">
        {{ item.filename }}
      </a-button>
      <Progress v-if="item.percent > 0" size="small" :percent="item.percent" :show-info="false" :status="getStatus(item.status)" />
      <a-button
        v-if="item.percent > 0 && item.percent < 100"
        type="link"
        @click="cancelDownload(item)"
      >
        <template v-if="item.status === AppFileStatus.cancled">
          已取消
        </template>
        <template v-else>
          取消下载
        </template>
      </a-button>
    </div>
  </template>
  <span v-else>暂无附件</span>
</template>

<style lang="scss" scoped>
:deep(.ant-progress) {
  width: 100px;
  margin: 0;
}
</style>
