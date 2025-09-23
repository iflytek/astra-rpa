import { Typography } from 'ant-design-vue'
import { defineComponent } from 'vue'

import './style.scss'

export const RichTextPreview = defineComponent({
  name: 'RichTextPreview',
  props: {
    content: {
      type: String,
      required: true,
    },
    classes: {
      type: String,
      default: '',
    },
  },
  setup(props) {
    return () => (
      <Typography>
        <div class={`tiptap ${props.classes}`} v-html={props.content} />
      </Typography>
    )
  },
})
