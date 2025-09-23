<script setup lang="ts">
import { Input } from 'ant-design-vue'
import { ref } from 'vue'

const { marketName } = defineProps({
  marketName: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['change'])

const fireTeamName = ref('')

function changefireTeamName() {
  emit && emit('change', fireTeamName.value)
}
</script>

<template>
  <div class="modal-form">
    <div class="modal-form">
      <div class="modal-form-title">
        确定解散“{{ marketName }}”吗？
      </div>
      <Input
        v-model:value="fireTeamName"
        class="modal-form-input"
        placeholder="请输入要解散的团队名称"
        :max-length="20"
        @change="changefireTeamName"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
</style>
