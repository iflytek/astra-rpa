import { Button, Tooltip } from 'ant-design-vue'
import { defineComponent } from 'vue'
import type { SlotsType } from 'vue'

export const ButtonLink = defineComponent({
  name: 'ButtonLink',
  props: {
    tooltip: String,
    disabled: Boolean,
  },
  // biome-ignore lint/suspicious/noExplicitAny: <explanation>
  slots: Object as SlotsType<{ default: any, icon: any }>,
  emits: ['click'],
  setup(props, { slots, emit }) {
    return () => {
      const ButtonItem = (
        <Button
          disabled={props.disabled}
          class="inline-flex items-center justify-center space-x-1 m-0 p-0 h-4 leading-4 text-xs cursor-pointer text-[rgba(0,0,0,0.85)] hover:!text-[#4e68f6]"
          type="link"
          onClick={() => emit('click')}
        >
          {slots.icon?.()}
          {slots.default?.()}
        </Button>
      )

      if (!props.tooltip) {
        return (
          <Tooltip placement="top" title={props.tooltip}>
            {ButtonItem}
          </Tooltip>
        )
      }

      return ButtonItem
    }
  },
})
