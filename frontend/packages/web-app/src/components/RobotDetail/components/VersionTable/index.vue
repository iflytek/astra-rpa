<script setup lang="ts">
import { Badge, Table } from 'ant-design-vue'
import type { ColumnsType } from 'ant-design-vue/es/table'
import type { PropType } from 'vue'

export interface Version {
  versionNum: number
  createTime: string
  online: number
}

const props = defineProps({
  versionList: {
    type: Array as PropType<Version[]>,
    required: true,
  },
})

const versionTableColumns: ColumnsType = [
  { dataIndex: 'versionNum', key: 'version' },
  { dataIndex: 'createTime', key: 'createTime' },
  { dataIndex: 'status', key: 'online' },
]
</script>

<template>
  <Table
    :columns="versionTableColumns"
    :data-source="props.versionList"
    size="small"
    :show-header="false"
    :pagination="false"
    :scroll="{ y: 120 }"
  >
    <template #bodyCell="{ column, record }">
      <template v-if="column.key === 'version'">
        <span>版本{{ record.versionNum }}</span>
      </template>
      <template v-if="column.key === 'online' && record.online === 1">
        <Badge status="success" text="当前启用版本" />
      </template>
    </template>
  </Table>
</template>
