import type { Meta, StoryObj } from '@storybook/vue3-vite'

import { CodeEditor } from './index'

const meta = {
  title: 'Example/CodeEditor',
  component: CodeEditor,
} satisfies Meta<typeof CodeEditor>

export default meta
type Story = StoryObj<typeof meta>

export const Primary: Story = {
  args: {
    isDark: false,
    projectId: '1855905608182833152',
    height: '300px',
    value: `# This sample demonstrates how common errors can be detected statically by pyright.

def add(x: float, y: float):
    return x + y

# Passing a str instance as the second argument results in a runtime exception.
add(1, "")
    `,
  },
}
