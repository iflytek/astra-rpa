<script lang="tsx">
import { Form } from 'ant-design-vue'
import { reactive } from 'vue'

import useConfigFormItem from '../hooks/createConfigFormItem'

export default {
  name: 'FormItem',
  components: {},
  props: {
    option: {
      type: Object,
      default() {
        return {}
      },
    },
  },
  setup(props) {
    const { createItemFn } = useConfigFormItem()
    const { option } = reactive({
      ...props,
    })
    const IntroFn = () => {
      return (
        <Form.Item>
          {createItemFn[option.dialogFormType](option)}
        </Form.Item>
      )
    }
    return () => IntroFn()
  },
}
</script>

<style lang="scss" scoped>
.ant-form-item {
  margin-bottom: 5px;
}
</style>
