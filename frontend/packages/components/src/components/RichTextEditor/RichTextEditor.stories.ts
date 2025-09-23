import type { Meta, StoryObj } from '@storybook/vue3-vite'

import { RichTextEditor } from './index'

const meta = {
  title: 'Example/RichTextEditor',
  component: RichTextEditor,
} satisfies Meta<typeof RichTextEditor>

export default meta
type Story = StoryObj<typeof meta>

export const Primary: Story = {
  args: {
    value: '<p>I’m running Tiptap with Vue.js. 🎉</p>',
    placeholder: '请输入使用说明...',
    uploadFile: file => Promise.resolve(URL.createObjectURL(file)),
  },
}
