<script setup lang="ts">
import type { PropType } from 'vue'

import { Button, Checkbox, message } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { computed, defineAsyncComponent, ref, useTemplateRef } from 'vue'

import { releaseWithPublish } from '@/api/market'
import { publishRobot } from '@/api/robot'
import { useCommonOperate } from '@/views/Home/pages/hooks/useCommonOperate'

import type BasicForm from './BasicForm.vue'
import type { FormState } from './utils'

import { toBackData } from './utils'

const props = defineProps({
  robotId: {
    type: String,
    required: true,
  },
  defaultData: Object as PropType<FormState>,
})

const emits = defineEmits(['submited'])
const BasicFormComponent = defineAsyncComponent(() => import('./BasicForm.vue'))
const { t } = useTranslation()
const { applicationReleaseCheck } = useCommonOperate()

const isFirstVerison = computed(() => props.defaultData?.version === 1)

const basicFormData = ref<FormState>(props.defaultData)
const basicFormRef
  = useTemplateRef<InstanceType<typeof BasicForm>>('basicForm')
const enableLastVersion = ref(isFirstVerison.value)

async function handleSubmit(): Promise<void> {
  await basicFormRef.value.validate()

  const lastPublishData = {
    robotId: props.robotId,
    ...toBackData({
      ...basicFormData.value,
      enableLastVersion: enableLastVersion.value,
    }),
  }
  console.log('lastPublishData', lastPublishData)

  const res = await publishRobot(lastPublishData)
  message.success('发版成功')

  // // 检查是否需要上架申请(如果开启上架审核且分享过市场, 需弹窗提示是否要发起上架申请，用户确认后发起上架申请)
  // applicationReleaseCheck({
  //   robotId: lastPublishData.robotId,
  //   version: lastPublishData.version,
  //   source: 'publish',
  // }, async (params) => {
  //   // 需要上架申请
  //   const releaseRes = await releaseWithPublish({ robotId: lastPublishData.robotId, robotVersion: lastPublishData.version, name: lastPublishData.name, ...params }) as { data?: string }
  //   message.success(releaseRes.data || '当前机器人自动通过上架审核，请至应用市场查看更新')
  // }, () => { // 不需要上架申请, 原发版逻辑
  //   // 如果分享过市场，data内容为market，如果没分享过，内容为create，对应两种提示
  //   if (Number(basicFormData.value.version) > 1 && res.data === 'market') {
  //     message.success('当前机器人发版更新已自动同步到应用市场')
  //   }
  // })
  emits('submited')
}
</script>

<template>
  <div class="publish-container w-full h-full flex flex-col overflow-hidden pt-5">
    <div class="publish-content flex-1 overflow-y-auto h-full">
      <div class="basic-form">
        <BasicFormComponent
          ref="basicForm"
          v-model="basicFormData"
          :robot-id="props.robotId"
        />
      </div>
    </div>
    <div class="publish-footer flex h-[60px] items-center justify-between px-6">
      <Checkbox v-if="!isFirstVerison" v-model:checked="enableLastVersion">
        同步启用该版本
      </Checkbox>
      <Button type="primary" @click="handleSubmit">
        {{ t('publish') }}
      </Button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.publish-container {
  background: $color-bg-container;
}
.publish-header {
  height: 64px;
  line-height: 64px;
  margin-right: 36px;
}
.publish-content {
  &::webkit-scrollbar {
    display: none;
  }
}
.title {
  font-size: 18px;
  font-weight: 600;
}
</style>
