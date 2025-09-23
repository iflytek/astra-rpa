/** @format */

import { DeleteOutlined, SearchOutlined } from '@ant-design/icons-vue'
import { Tooltip } from 'ant-design-vue'
import { useTranslation } from 'i18next-vue'
import { reactive } from 'vue'

import type { TaskTrigger } from '@/types/schedule'

import { TASK_TYPE, TASK_TYPE_OPTION, WEEK_MAP } from '../../config/task'

import useQueueOperation from './useQueueOperation'

export default function useQueueTableOption() {
  const { t } = useTranslation()

  const { queueTableRef, rowSelection, deleteQueueTask, getTableData, batchDelete, queueSetting, refreshQueueList, intervalRefresh } = useQueueOperation()

  const weekRender = (value: any[]) => {
    const sortWeek = value.sort()
    const weeks = sortWeek.map(item => WEEK_MAP[item]).join('、')
    return weeks
  }

  const conditionInfoRender = (record) => {
    try {
      const taskJson = JSON.parse(record.trigger_json) as TaskTrigger
      switch (record.task_type) {
        case TASK_TYPE.TASK_TIME:
          if (taskJson.frequency_flag === 'advance') {
            return t('taskCondition.advance', { cron_expression: taskJson.cron_expression })
          }
          if (taskJson.frequency_flag === 'regular') {
            return t('taskCondition.regular', { time_expression: taskJson.time_expression })
          }
          if (taskJson.frequency_flag === 'minutes') {
            return t('taskCondition.minutes', { minutes: taskJson.minutes })
          }
          if (taskJson.frequency_flag === 'hours') {
            return t('taskCondition.hours', { hours: taskJson.hours, minutes: taskJson.minutes })
          }
          if (taskJson.frequency_flag === 'days') {
            return t('taskCondition.days', { hours: taskJson.hours, minutes: taskJson.minutes })
          }
          if (taskJson.frequency_flag === 'weeks') {
            return t('taskCondition.weeks', { weeks: weekRender(taskJson.weeks), hours: taskJson.hours, minutes: taskJson.minutes })
          }
          if (taskJson.frequency_flag === 'months') {
            return t('taskCondition.months', { months: taskJson.months, weeks: weekRender(taskJson.weeks), hours: taskJson.hours, minutes: taskJson.minutes })
          }
          break
        case TASK_TYPE.TASK_MANUAL:
          return t('taskCondition.manual')
        case TASK_TYPE.TASK_FILE:
          return t('taskCondition.file', { directory: taskJson.directory })
        case TASK_TYPE.TASK_HOTKEY:
          return t('taskCondition.hotKey', { shortcuts: taskJson.shortcuts.join(' + ') })
        case TASK_TYPE.TASK_MAIL:
          return t('taskCondition.mail', { interval_time: taskJson.interval_time })
        default:
          return t('taskCondition.unknown')
      }
    }
    catch (error) {
      console.error(`conditionInfoRender: ${error}`)
    }
  }
  const excuteConditionRender = ({ record }) => {
    const taskType = t(`taskTypeOption.${record.task_type}`)
    const taskInfo = conditionInfoRender(record)
    return (
      <div>
        <div class="flex items-center h-6">
          <span class="">{ taskType }</span>
        </div>
        <Tooltip title={taskInfo}>
          <div class="text-sm text-text-secondary truncate max-w-[200px]">{ taskInfo }</div>
        </Tooltip>
      </div>
    )
  }
  const taskOperationRender = ({ record }) => {
    record.enable = !!record.enable // 后端传不了布尔值，只能传整数，所以这里转换一下
    return (
      <div class="operation text-base">
        <Tooltip title={t('delete')}>
          <DeleteOutlined
            class="ml-4"
            onClick={() => {
              deleteQueueTask(record)
            }}
          />
        </Tooltip>
      </div>
    )
  }
  const optionHeight = window.innerHeight - 75
  const tableOption = reactive({
    height: optionHeight, // 包含header,table,footer三部分高度
    refresh: false, // 控制表格数据刷新
    getData: getTableData,
    formList: [
      // {
      //   componentType: 'back',
      //   bind: 'back',
      //   label: '',
      //   clickFn: () => {
      //     emit('back')
      //   },
      // },
      {
        componentType: 'input',
        bind: 'name',
        placeholder: t('taskNamePlaceholder'),
        prefix: <SearchOutlined />,
      },
      {
        componentType: 'select',
        bind: 'taskType',
        placeholder: t('taskTypePlaceholder'),
        span: 24,
        options: [
          {
            label: t('all'),
            value: '',
          },
          ...TASK_TYPE_OPTION.filter(i => i.value !== TASK_TYPE.TASK_MANUAL).map((i) => {
            return {
              label: t(`taskTypeOption.${i.value}`),
              value: i.value,
            }
          }), // 手动触发不在队列中
        ],
        // hidden: true,
      },
    ],
    buttonList: [
      // 表格上方的按钮配置
      {
        label: t('refresh'),
        action: '',
        clickFn: refreshQueueList,
        type: 'default',
        hidden: false,
      },
      {
        label: t('batchDelete'),
        action: '',
        clickFn: batchDelete,
        type: 'default',
        hidden: false,
      },
      {
        label: t('queueSetting'),
        action: '',
        clickFn: queueSetting,
        type: 'primary',
        hidden: false,
      },

    ],
    tableProps: {
      // 表格配置，即antd中的Table组件的属性
      columns: [
        {
          title: t('executeOrder'),
          dataIndex: 'status_index',
          key: 'status_index',
          width: 90,
          align: 'center',
        },
        {
          title: t('taskName'),
          dataIndex: 'trigger_name',
          key: 'trigger_name',
          ellipsis: true,
        },
        {
          title: t('robot'),
          dataIndex: 'callback_project_ids',
          key: 'callback_project_ids',
          ellipsis: true,
          customRender: ({ record }) => {
            const robotNames = record.callback_project_ids.map(i => i.robotName).join('，')
            return <Tooltip title={robotNames}>{ robotNames }</Tooltip>
          },
        },
        {
          title: `${t('queueTime')}/${t('expireTime')}`,
          dataIndex: 'enqueue_time',
          key: 'enqueue_time',
          ellipsis: true,
          customRender: ({ record }) => {
            return (
              <div class="enqueue_time_and_expire_time">
                <Tooltip title={record.enqueue_time}>{ record.enqueue_time }</Tooltip>
                <br />
                <Tooltip title={record.expire_time}>{ record.expire_time }</Tooltip>
              </div>
            )
          },
        },
        {
          title: t('excuteCondition'),
          dataIndex: 'task_type',
          key: 'task_type',
          ellipsis: true,
          width: 200,
          customRender: ({ record }) => {
            return excuteConditionRender({ record })
          },
        },
        {
          title: t('operate'),
          dataIndex: 'oper',
          key: 'oper',
          width: 70,
          customRender: ({ record }) => {
            return taskOperationRender({ record })
          },
        },
      ],
      rowKey: 'unique_id',
      rowSelection,
      scroll: { y: optionHeight - 160 },
    },
    params: {
      // 绑定的表单配置的数据
      // taskSelect: 'all',
      name: '',
    },
    emptyText: t('queueListEmpty'),
  })

  return { tableOption, queueTableRef, intervalRefresh }
}
