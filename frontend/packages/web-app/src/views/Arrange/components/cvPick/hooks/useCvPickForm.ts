import type { Rule } from 'ant-design-vue/es/form'
import { ref } from 'vue'

export function useCvPickForm() {
  const formRef = ref()
  const formOption = ref({
    pickName: '',
  })
  const rules: Record<string, Rule[]> = {
    pickName: [
      { required: true, message: '请输入元素名称', trigger: 'blur' },
    ],
  }
  const setFormOption = (data: any) => {
    formOption.value = { ...formOption.value, ...data }
  }
  const validateForm = (callback) => {
    formRef.value.validate().then((valid) => {
      if (valid) {
        callback && callback()
      }
    })
  }

  return {
    formRef,
    formOption,
    rules,
    setFormOption,
    validateForm,
  }
}
