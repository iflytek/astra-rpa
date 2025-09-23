import type { Meta, StoryObj } from '@storybook/vue3-vite'

import { Icon } from './index'

const meta = {
  title: 'Example/Icon',
  component: Icon,
} satisfies Meta<typeof Icon>

export default meta
type Story = StoryObj<typeof meta>

export const Primary: Story = {
  args: {
    name: 'user',
    class: 'icon',
    style: 'width: 100px; height: 100px;',
  },
}
