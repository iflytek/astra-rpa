import { TableOutlined } from '@ant-design/icons-vue'
import type { Editor } from '@tiptap/vue-3'
import { Popover } from 'ant-design-vue'
import { computed, defineComponent, ref } from 'vue'
import type { PropType } from 'vue'

import { IconButton } from '../../IconButton'

export const TableToolbar = defineComponent({
  name: 'TableToolbar',
  props: {
    editor: {
      type: Object as PropType<Editor>,
      required: true,
    },
  },
  setup({ editor }) {
    const open = ref(false)
    const hoveredSize = ref({ rows: 1, cols: 1 })
    const minSize = 4
    const maxSize = 10

    const containerSize = computed(() => ({
      rows: Math.max(minSize, Math.min(hoveredSize.value.rows + 1, maxSize)),
      cols: Math.max(minSize, Math.min(hoveredSize.value.cols + 1, maxSize)),
    }))

    const handleMouseEnter = (row: number, col: number) => {
      hoveredSize.value = { rows: row + 1, cols: col + 1 }
    }

    const handleMouseLeave = () => {
      hoveredSize.value = { rows: 1, cols: 1 }
    }

    const handleOpenChange = (_open: boolean) => {
      open.value = _open
    }

    const handleClick = () => {
      const bol = editor.chain().focus().insertTable({ ...hoveredSize.value, withHeaderRow: true }).run()

      bol && (open.value = false)
    }

    const renderContent = () => (
      <div
        onMouseleave={handleMouseLeave}
      >
        <table class="border-collapse cursor-pointer border border-border border-gray-300">
          <tbody>
            {Array.from({ length: containerSize.value.rows }, (_, row) => (
              <tr key={row}>
                {Array.from({ length: containerSize.value.cols }, (_, col) => (
                  <td
                    key={`${row}-${col}`}
                    class={[
                      'w-5 h-5 border-r border-b border-border',
                      row < hoveredSize.value.rows && col < hoveredSize.value.cols ? 'bg-primary-bg-hover' : 'bg-bg-container',
                      row === containerSize.value.rows - 1 ? 'border-b-0' : '',
                      col === containerSize.value.cols - 1 ? 'border-r-0' : '',
                    ]}
                    onMouseenter={() => handleMouseEnter(row, col)}
                    onClick={handleClick}
                  />
                ))}
              </tr>
            ))}
          </tbody>
        </table>

        <div class="text-center mt-1">
          {`${hoveredSize.value.rows} x ${hoveredSize.value.cols}`}
        </div>
      </div>
    )

    return () => (
      <Popover
        open={open.value}
        arrow={false}
        content={renderContent()}
        placement="bottomLeft"
        trigger="click"
        onOpenChange={handleOpenChange}
      >
        <IconButton title="表格">
          <TableOutlined />
        </IconButton>
      </Popover>
    )
  },
})
