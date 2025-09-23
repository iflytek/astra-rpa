import {
  computed,
  defineComponent,

} from 'vue'
import type { SlotsType, StyleValue } from 'vue'

import { panelProps } from './interface'

export const Panel = defineComponent({
  name: 'SplitterPanel',
  props: panelProps(),
  slots: Object as SlotsType<{
    // biome-ignore lint/suspicious/noExplicitAny: <explanation>
    default: any
  }>,
  setup(props, { slots }) {
    const style = computed<StyleValue>(() => {
      const hasSize = props.size !== undefined
      const isString = typeof props.size === 'string'

      return {
        flexBasis: hasSize ? `${props.size}${isString ? '' : 'px'}` : 'auto',
        flexGrow: hasSize ? 0 : 1,
      }
    })

    const prefixCls = computed(() => props.prefixCls || 'splitter')

    return () => (
      <div
        style={style.value}
        class={[
          `${prefixCls.value}-panel`,
          { [`${prefixCls.value}-panel-hidden`]: props.size === 0 },
        ]}
      >
        {slots.default?.()}
      </div>
    )
  },
})
