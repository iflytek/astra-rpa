import { LinkOutlined } from '@ant-design/icons-vue'
import type { Editor } from '@tiptap/vue-3'
import { Button, Form, Input, Popover } from 'ant-design-vue'
import type { PropType } from 'vue'
import { defineComponent, reactive, ref } from 'vue'

import { IconButton } from '../../IconButton'

interface FormState {
  text: string
  url: string
}

export const LinkToolbar = defineComponent({
  name: 'LinkToolbar',
  props: {
    editor: {
      type: Object as PropType<Editor>,
      required: true,
    },
  },
  setup(props) {
    const { editor } = props
    const open = ref(false)
    const formState = reactive<Partial<FormState>>({})

    const onFinish = () => {
      const { text, url } = formState
      if (text && url) {
        editor.chain().focus().deleteSelection().insertContent(text).run()
        const position = editor.state.selection.$anchor.pos - text.length
        editor.chain().focus().setTextSelection({ from: position, to: position + text.length }).setLink({ href: url }).run()

        open.value = false
      }
    }

    const renderContent = () => (
      <Form layout="vertical" model={formState} onFinish={onFinish} class="w-80">
        <Form.Item label="文本">
          <Input v-model={[formState.text, 'value']} placeholder="添加描述" />
        </Form.Item>
        <Form.Item label="链接">
          <Input v-model={[formState.url, 'value']} placeholder="链接地址" />
        </Form.Item>
        <Form.Item class="m-0">
          <Button htmlType="submit" disabled={!formState.text || !formState.url}>确定</Button>
        </Form.Item>
      </Form>
    )

    const handleOpenChange = (_open: boolean) => {
      open.value = _open

      if (_open) {
        const selection = editor.state.selection
        const { from, to } = selection
        formState.text = editor.state.doc.textBetween(from, to, ' ')
        formState.url = editor.getAttributes('link').href
      }
    }

    return () => (
      <Popover
        open={open.value}
        arrow={false}
        content={renderContent()}
        placement="bottomLeft"
        trigger="click"
        onOpenChange={handleOpenChange}
      >
        <IconButton title="插入链接">
          <LinkOutlined />
        </IconButton>
      </Popover>
    )
  },
})
