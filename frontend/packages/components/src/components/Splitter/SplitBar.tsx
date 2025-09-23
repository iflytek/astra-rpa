import { DownOutlined, LeftOutlined, RightOutlined, UpOutlined } from '@ant-design/icons-vue'
import { computed, defineComponent, ref, watchEffect } from 'vue'

import { functionType } from '../../utils/type'

export const SplitBar = defineComponent({
  name: 'SplitBar',
  props: {
    index: { type: Number, required: true },
    active: { type: Boolean, required: true },
    prefixCls: { type: String, required: true },
    resizable: { type: Boolean, required: true },
    startCollapsible: { type: Boolean, required: true },
    endCollapsible: { type: Boolean, required: true },
    vertical: { type: Boolean, required: true },
    ariaNow: { type: Number, required: true },
    ariaMin: { type: Number, required: true },
    ariaMax: { type: Number, required: true },
    lazy: Boolean,
    containerSize: { type: Number, required: true },
    onOffsetStart: functionType<(index: number) => void>(),
    onOffsetUpdate:
      functionType<(index: number, offsetX: number, offsetY: number) => void>(),
    onOffsetEnd: functionType<() => void>(),
    onCollapse: functionType<(index: number, type: 'start' | 'end') => void>(),
  },
  setup(props) {
    function getValidNumber(num: number | undefined): number {
      return typeof num === 'number' && !Number.isNaN(num)
        ? Math.round(num)
        : 0
    }

    // ======================== Resize ========================
    const startPos = ref<[x: number, y: number] | null>(null)
    const constrainedOffset = ref<number>(0)

    const constrainedOffsetX = computed(() =>
      props.vertical ? 0 : constrainedOffset.value,
    )
    const constrainedOffsetY = computed(() =>
      props.vertical ? constrainedOffset.value : 0,
    )

    function onMouseDown(e: MouseEvent) {
      if (props.resizable && e.currentTarget) {
        startPos.value = [e.pageX, e.pageY]
        props.onOffsetStart(props.index)
      }
    }

    function onTouchStart(e: TouchEvent) {
      if (props.resizable && e.touches.length === 1) {
        const touch = e.touches[0]
        startPos.value = [touch.pageX, touch.pageY]
        props.onOffsetStart(props.index)
      }
    }

    // Updated constraint calculation
    function getConstrainedOffset(rawOffset: number) {
      const currentPos = (props.containerSize * props.ariaNow) / 100
      const newPos = currentPos + rawOffset

      // Calculate available space
      const minAllowed = Math.max(
        0,
        (props.containerSize * props.ariaMin) / 100,
      )
      const maxAllowed = Math.min(
        props.containerSize,
        (props.containerSize * props.ariaMax) / 100,
      )

      // Constrain new position within bounds
      const clampedPos = Math.max(minAllowed, Math.min(maxAllowed, newPos))
      return clampedPos - currentPos
    }

    function handleLazyMove(offsetX: number, offsetY: number) {
      const constrainedOffsetValue = getConstrainedOffset(
        props.vertical ? offsetY : offsetX,
      )
      constrainedOffset.value = constrainedOffsetValue
    }

    function handleLazyEnd() {
      props.onOffsetUpdate(
        props.index,
        constrainedOffsetX.value,
        constrainedOffsetY.value,
      )
      constrainedOffset.value = 0
    }

    watchEffect((onCleanup) => {
      if (startPos.value) {
        const onMouseUpAndTouchEnd = () => {
          if (props.lazy) {
            handleLazyEnd()
          }

          startPos.value = null
          props.onOffsetEnd()
        }

        const handleCommonMove = (pageX: number, pageY: number) => {
          const offsetX = pageX - (startPos.value ? startPos.value[0] : 0)
          const offsetY = pageY - (startPos.value ? startPos.value[1] : 0)

          if (props.lazy) {
            handleLazyMove(offsetX, offsetY)
          }
          else {
            props.onOffsetUpdate(props.index, offsetX, offsetY)
          }
        }

        const onMouseMove = (e: MouseEvent) =>
          handleCommonMove(e.pageX, e.pageY)

        const handleTouchMove = (e: TouchEvent) => {
          if (e.touches.length === 1) {
            const touch = e.touches[0]
            handleCommonMove(touch.pageX, touch.pageY)
          }
        }

        window.addEventListener('touchmove', handleTouchMove)
        window.addEventListener('touchend', onMouseUpAndTouchEnd)
        window.addEventListener('mousemove', onMouseMove)
        window.addEventListener('mouseup', onMouseUpAndTouchEnd)

        onCleanup(() => {
          window.removeEventListener('mousemove', onMouseMove)
          window.removeEventListener('mouseup', onMouseUpAndTouchEnd)
          window.removeEventListener('touchmove', handleTouchMove)
          window.removeEventListener('touchend', onMouseUpAndTouchEnd)
        })
      }
    })

    return () => {
      const splitBarPrefixCls = `${props.prefixCls}-bar`

      const transformStyle = {
        [`--${splitBarPrefixCls}-preview-offset`]: `${constrainedOffset}px`,
      }

      // ======================== Render ========================
      const StartIcon = props.vertical ? UpOutlined : LeftOutlined
      const EndIcon = props.vertical ? DownOutlined : RightOutlined

      return (
        <div
          class={splitBarPrefixCls}
          aria-valuenow={getValidNumber(props.ariaNow)}
          aria-valuemin={getValidNumber(props.ariaMin)}
          aria-valuemax={getValidNumber(props.ariaMax)}
        >
          {props.lazy && (
            <div
              class={[
                `${splitBarPrefixCls}-preview`,
                {
                  [`${splitBarPrefixCls}-preview-active`]: !!constrainedOffset,
                },
              ]}
              style={transformStyle}
            />
          )}

          <div
            class={[
              `${splitBarPrefixCls}-dragger`,
              {
                [`${splitBarPrefixCls}-dragger-disabled`]: !props.resizable,
                [`${splitBarPrefixCls}-dragger-active`]: props.active,
              },
            ]}
            onMousedown={onMouseDown}
            onTouchstart={onTouchStart}
          />

          {/* Start Collapsible */}
          {props.startCollapsible && (
            // biome-ignore lint/a11y/useKeyWithClickEvents: <explanation>
            <div
              class={[`${splitBarPrefixCls}-collapse-bar`, `${splitBarPrefixCls}-collapse-bar-start`]}
              onClick={() => props.onCollapse(props.index, 'start')}
            >
              <StartIcon
                class={[`${splitBarPrefixCls}-collapse-icon`, `${splitBarPrefixCls}-collapse-start`]}
              />
            </div>
          )}

          {/* End Collapsible */}
          {props.endCollapsible && (
            // biome-ignore lint/a11y/useKeyWithClickEvents: <explanation>
            <div
              class={[`${splitBarPrefixCls}-collapse-bar`, `${splitBarPrefixCls}-collapse-bar-end`]}
              onClick={() => props.onCollapse(props.index, 'end')}
            >
              <EndIcon
                class={[`${splitBarPrefixCls}-collapse-icon`, `${splitBarPrefixCls}-collapse-end`]}
              />
            </div>
          )}
        </div>
      )
    }
  },
})
