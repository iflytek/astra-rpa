<script lang="ts" setup>
import CvPickBtn from '@/views/Arrange/components/cvPick/CvPickBtn.vue'
import CvUploadBtn from '@/views/Arrange/components/cvPick/CvUploadBtn.vue'

import ElementManageHeader from '../ElementManageHeader.vue'
</script>

<template>
  <ElementManageHeader element-type="cv">
    <template #btns>
      <CvPickBtn class="mr-2" />
      <CvUploadBtn />
    </template>
  </ElementManageHeader>
</template>
