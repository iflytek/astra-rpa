import { SearchOutlined } from '@ant-design/icons-vue'
import { h } from 'vue'

function filterOption(input: string, option: any) {
  return option.children().some((option) => {
    return option.toLowerCase().includes(input.toLowerCase())
  })
}

export function useCardsTools() {
  const formList = [
    {
      componentType: 'input',
      bind: 'appName',
      placeholder: 'market.enterApplicationName',
      prefix: h(SearchOutlined),
    },
    {
      componentType: 'select',
      bind: 'creatorId',
      options: [],
      labelKey: 'name',
      valueKey: 'userId',
      showSearch: true,
      filterOption,
      style: 'width: 180px;',
      allowClear: true,
      placeholder: 'market.selectPublisher',
    },
    {
      componentType: 'select',
      bind: 'sortKey',
      options: [
        {
          label: 'market.latestRelease',
          value: 'createTime',
        },
        {
          label: 'market.mostDownload',
          value: 'downloadNum',
        },
        {
          label: 'market.mostView',
          value: 'checkNum',
        },
      ],
      placeholder: 'market.selectSort',
    },
  ]

  return { formList }
}
