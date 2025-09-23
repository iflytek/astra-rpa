import { InfoCircleOutlined, UserOutlined } from '@ant-design/icons-vue'
import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { Input, Space, Tooltip } from 'ant-design-vue'
import { ref } from 'vue'

const meta = {
  title: 'Antdv/Input',
  component: Input,
} satisfies Meta<typeof Input>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => ({
    components: { Input, Space, Tooltip, UserOutlined, InfoCircleOutlined },
    setup() {
      const value = ref<string>('')
      const userName = ref<string>('')

      return { value, userName }
    },
    template: `
      <div class="h-screen p-4 flex flex-col gap-4" style="background: black;">
        <Input v-model:value="value" placeholder="Basic usage" />
        <Input v-model:value="userName" placeholder="Basic usage">
          <template #prefix>
            <UserOutlined />
          </template>
          <template #suffix>
            <Tooltip title="Extra information">
              <InfoCircleOutlined />
            </Tooltip>
          </template>
        </Input>
      </div>
    `,
  }),
}
