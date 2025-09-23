import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { Select, SelectOption, Space } from 'ant-design-vue'
import type { SelectProps } from 'ant-design-vue'
import { ref } from 'vue'

const meta = {
  title: 'Antdv/Select',
  component: Select,
} satisfies Meta<typeof Select>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => ({
    components: { Select, SelectOption, Space },
    setup() {
      const value1 = ref('lucy')
      const value2 = ref('lucy')
      const value3 = ref('lucy')

      const options1 = ref<SelectProps['options']>([
        {
          value: 'jack',
          label: 'Jack',
        },
        {
          value: 'lucy',
          label: 'Lucy',
        },
        {
          value: 'disabled',
          label: 'Disabled',
          disabled: true,
        },
        {
          value: 'yiminghe',
          label: 'Yiminghe',
        },
      ])
      const options2 = ref<SelectProps['options']>([
        {
          value: 'lucy',
          label: 'Lucy',
        },
      ])
      const options3 = ref<SelectProps['options']>([
        {
          value: 'lucy',
          label: 'Lucy',
        },
      ])
      const focus = () => {
        console.log('focus')
      }

      const handleChange = (value: string) => {
        console.log(`selected ${value}`)
      }

      return {
        value1,
        value2,
        value3,
        options1,
        options2,
        options3,
        focus,
        handleChange,
      }
    },
    template: `
    <h2>use a-select-option</h2>
     <Space>
       <Select
         ref="select"
         v-model:value="value1"
         style="width: 120px"
         @focus="focus"
         @change="handleChange"
       >
         <SelectOption value="jack">Jack</SelectOption>
         <SelectOption value="lucy">Lucy</SelectOption>
         <SelectOption value="disabled" disabled>Disabled</SelectOption>
         <SelectOption value="Yiminghe">yiminghe</SelectOption>
       </Select>
       <Select v-model:value="value2" style="width: 120px" disabled>
         <SelectOption value="lucy">Lucy</SelectOption>
       </Select>
       <Select v-model:value="value3" style="width: 120px" loading>
         <SelectOption value="lucy">Lucy</SelectOption>
       </Select>
     </Space>
     <h2 style="margin-top: 10px">use options (recommend)</h2>
     <Space>
       <Select
         ref="select"
         v-model:value="value1"
         style="width: 120px"
         :options="options1"
         @focus="focus"
         @change="handleChange"
       ></Select>
       <Select v-model:value="value2" style="width: 120px" disabled :options="options2"></Select>
       <Select v-model:value="value3" style="width: 120px" loading :options="options3"></Select>
     </Space>
    `,
  }),
}
