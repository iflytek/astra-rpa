import { ProfileOutlined } from '@ant-design/icons-vue'
import { Button, Table, Tooltip } from 'ant-design-vue'

import { getDurationText } from '@/utils/dayjsUtils'

import { getTaskExecuteLst } from '@/api/task'
import StatusCircle from '@/views/Home/components/StatusCircle.vue'
import { useCommonOperate } from '@/views/Home/pages/hooks/useCommonOperate.tsx'
import type { resOption } from '@/views/Home/types'

export default function useTaskRecordOperation() {
  const { handleCheck } = useCommonOperate()
  function getTableData(params) {
    return new Promise((resolve) => {
      getTaskExecuteLst(params).then((res: resOption) => {
        const { data } = res
        if (data) {
          const { total, records } = data
          resolve({
            records,
            total,
          })
        }
      })
    })
  }

  function handleExpandedRowRender({ record }) {
    const innerColumns = [
      {
        title: '机器人名称',
        dataIndex: 'robotName',
        key: 'robotName',
        ellipsis: true,
      },
      {
        title: '机器人版本',
        key: 'robotVersion',
        dataIndex: 'robotVersion',
        ellipsis: true,
        customRender: ({ record }) => `版本${record.robotVersion}`,
      },
      {
        title: '开始时间',
        key: 'startTime',
        dataIndex: 'startTime',
        width: 170,
      },
      {
        title: '结束时间',
        key: 'endTime',
        dataIndex: 'endTime',
        width: 170,
      },
      {
        title: '执行时长',
        key: 'executeTime',
        dataIndex: 'executeTime',
        customRender: ({ record }) => getDurationText(record.executeTime),
      },
      {
        title: '执行结果',
        key: 'result',
        dataIndex: 'result',
        customRender: ({ record }) => {
          return <StatusCircle type={`${record.result}`} />
        },
      },
      {
        title: '操作',
        dataIndex: 'oper',
        key: 'oper',
        customRender: ({ record }) => {
          return (
            <div class="operation">
              <Tooltip title="日志详情" placement="bottom">
                <Button
                  type="link"
                  style="margin-right: 10px;"
                  size="small"
                  onClick={() => handleCheck({ record })}
                >
                  <ProfileOutlined />
                </Button>
              </Tooltip>
            </div>
          )
        },
      },
    ]
    return (
      <Table
        rowKey="recordId"
        columns={innerColumns}
        dataSource={record.robotExecuteRecordList}
        pagination={false}
      />
    )
  }

  return {
    getTableData,
    handleExpandedRowRender,
  }
}
