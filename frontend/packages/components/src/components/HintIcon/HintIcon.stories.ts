import type { Meta, StoryObj } from '@storybook/vue3-vite'

import { HintIcon } from './index'

const meta = {
  title: 'Example/HintIcon',
  component: HintIcon,
} satisfies Meta<typeof HintIcon>

export default meta
type Story = StoryObj<typeof meta>

export const Primary: Story = {
  args: {
    name: 'user',
  },
}

export const Suffix: Story = {
  args: {
    name: 'user',
  },
  render: args => ({
    components: { HintIcon },
    setup() {
      return { args }
    },
    template: `
      <HintIcon v-bind="args">
        <template #suffix>
          <span class="ml-1">测试</span>
        </template>
      </HintIcon>
    `,
  }),
}
