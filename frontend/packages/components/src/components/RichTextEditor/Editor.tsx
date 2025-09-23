import { BoldOutlined, OrderedListOutlined, UnorderedListOutlined } from '@ant-design/icons-vue'
import Gapcursor from '@tiptap/extension-gapcursor'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import Placeholder from '@tiptap/extension-placeholder'
import Table from '@tiptap/extension-table'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import TableRow from '@tiptap/extension-table-row'
import StarterKit from '@tiptap/starter-kit'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import { Typography } from 'ant-design-vue'
import type { PropType } from 'vue'
import { defineComponent, onBeforeUnmount, watch } from 'vue'

import { IconButton } from '../IconButton'

import { HeadingToolbar } from './toolbar/HeadingToolbar'
import { ImageToolbar } from './toolbar/ImageToolbar'
import { LinkToolbar } from './toolbar/LinkToolbar'
import { TableToolbar } from './toolbar/TableToolbar'

import './style.scss'

export const RichTextEditor = defineComponent({
  name: 'RichTextEditor',
  props: {
    value: {
      type: String,
      default: '',
    },
    placeholder: String,
    height: {
      type: Number,
      default: 300,
    },
    uploadFile: {
      type: Function as PropType<(file: File) => Promise<string>>,
      required: true,
    },
  },
  emits: { 'update:value': (_value: string) => true },
  setup(props, { emit }) {
    const editor = useEditor({
      content: props.value,
      extensions: [
        StarterKit.configure({
          heading: {
            HTMLAttributes: {
              class: 'ant-typography',
            },
          },
          paragraph: {
            HTMLAttributes: {
              class: 'ant-typography',
            },
          },
        }),
        Image,
        Placeholder.configure({ placeholder: props.placeholder }),
        Link.configure({
          openOnClick: false,
          defaultProtocol: 'https',
          HTMLAttributes: {
            class: 'ant-typography',
          },
        }),
        Table.configure({
          resizable: true,
        }),
        TableRow.configure({
          HTMLAttributes: {
            class: 'ant-table-row',
          },
        }),
        TableHeader.configure({
          HTMLAttributes: {
            class: 'ant-table-cell ant-table-cell-header',
          },
        }),
        TableCell.configure({
          HTMLAttributes: {
            class: 'ant-table-cell',
          },
        }),
        Gapcursor,
      ],
      onUpdate: ({ editor }) => {
        emit('update:value', editor.getHTML())
      },
    })

    watch(() => props.value, (value) => {
      const isSame = editor.value?.getHTML() === value

      if (isSame)
        return

      editor.value?.commands.setContent(value, false)
    })

    onBeforeUnmount(() => {
      editor.value?.destroy()
    })

    return () => {
      if (!editor.value)
        return null

      return (
        <div class="p-0">
          <div class="h-10 border-b border-border flex items-center px-4 gap-2">
            <ImageToolbar editor={editor.value} uploadFile={props.uploadFile} />

            <HeadingToolbar editor={editor.value} />

            <IconButton title="加粗文字" active={editor.value?.isActive('bold')} onClick={() => editor.value?.chain().focus().toggleBold().run()}>
              <BoldOutlined />
            </IconButton>
            <IconButton title="有序列表" active={editor.value?.isActive('orderedList')} onClick={() => editor.value?.chain().focus().toggleOrderedList().run()}>
              <OrderedListOutlined />
            </IconButton>
            <IconButton title="无序列表" active={editor.value?.isActive('bulletList')} onClick={() => editor.value?.chain().focus().toggleBulletList().run()}>
              <UnorderedListOutlined />
            </IconButton>
            <TableToolbar editor={editor.value} />
            <LinkToolbar editor={editor.value} />
          </div>

          <Typography>
            <EditorContent editor={editor.value} class="p-4 w-full overflow-y-auto" style={`height: ${props.height}px`} />
          </Typography>
        </div>
      )
    }
  },
})
