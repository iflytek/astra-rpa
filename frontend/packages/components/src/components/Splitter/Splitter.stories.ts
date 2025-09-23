import type { Meta, StoryObj } from '@storybook/vue3-vite'
import { useElementSize } from '@vueuse/core'
import { Button, Switch } from 'ant-design-vue'
import { ref, useTemplateRef } from 'vue'

import { Panel } from './Panel'

import { Splitter } from './index'

const meta = {
  title: 'Example/Splitter',
  component: Splitter,
} satisfies Meta<typeof Splitter>

export default meta
type Story = StoryObj<typeof meta>

export const Primary: Story = {
  args: {},
  render: args => ({
    components: { Splitter, Panel },
    setup() {
      return { args }
    },
    template: `
      <Splitter :style="{ height: '200px', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }">
        <Panel defaultSize="40%" min="20%" max="70%" class="flex items-center justify-center">
          <span>First</span>
        </Panel>
        <Panel class="flex items-center justify-center">
          <span>Second</span>
        </Panel>
      </Splitter>
    `,
  }),
}

export const Control: Story = {
  args: {},
  render: args => ({
    components: { Switch, Splitter, Panel },
    setup() {
      const sizes = ref([30, 70])
      const enabled = ref(true)

      const handleResize = (_sizes: number[]) => {
        sizes.value = _sizes
      }

      return { args, enabled, sizes, handleResize }
    },
    template: `
      <Splitter @resize="handleResize" :style="{ height: '200px', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }">
        <Panel :size="sizes[0]" class="flex items-center justify-center" :resizable="enabled">
          <span>First</span>
        </Panel>
        <Panel :size="sizes[1]" class="flex items-center justify-center">
          <span>Second</span>
        </Panel>
      </Splitter>

      <Switch v-model:checked="enabled" class="mt-6" />
    `,
  }),
}

export const Vertical: Story = {
  args: {},
  render: args => ({
    components: { Splitter, Panel, Button },
    setup() {
      const container = useTemplateRef<HTMLElement>('container')
      const bottomSize = ref<Array<undefined | number>>([undefined, 30])
      const { height } = useElementSize(container)

      const handleResize = (_sizes: number[]) => {
        bottomSize.value = _sizes
      }

      const setBottomHeight = (_height: number) => {
        bottomSize.value = [height.value - _height, _height]
      }

      return { args, bottomSize, container, handleResize, setBottomHeight }
    },
    template: `
      <Splitter ref="container" @resize="handleResize" layout="vertical" :style="{ height: '300px', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }">
        <Panel :size="bottomSize[0]" class="flex items-center justify-center">
          <span>Top</span>
        </Panel>
        <Panel :size="bottomSize[1]" class="flex items-center justify-center">
          <span>Bottom</span>
        </Panel>
      </Splitter>

      <Button class="mt-4" @click="() => setBottomHeight(30)">30px</Button>
    `,
  }),
}

export const Multiple: Story = {
  args: {},
  render: args => ({
    components: { Splitter, Panel },
    setup() {
      return { args }
    },
    template: `
      <Splitter :style="{ height: '200px', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }">
        <Panel class="flex items-center justify-center">
          <span>Panel 1</span>
        </Panel>
        <Panel class="flex items-center justify-center">
          <span>Panel 2</span>
        </Panel>
        <Panel class="flex items-center justify-center">
          <span>Panel 3</span>
        </Panel>
      </Splitter>
    `,
  }),
}

export const Group: Story = {
  args: {},
  render: args => ({
    components: { Splitter, Panel },
    setup() {
      return { args }
    },
    template: `
      <Splitter :style="{ height: '300px', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }">
        <Panel class="flex items-center justify-center">
          <span>Left</span>
        </Panel>
        <Panel>
          <Splitter layout="vertical">
            <Panel class="flex items-center justify-center">
              <span>Top</span>
            </Panel>
            <Panel class="flex items-center justify-center">
              <span>Bottom</span>
            </Panel>
          </Splitter>
        </Panel>
      </Splitter>
    `,
  }),
}
