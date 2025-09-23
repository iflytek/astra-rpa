import { message } from 'ant-design-vue'
import { inject, nextTick, ref, watch } from 'vue'
import type { Ref } from 'vue'

import { editTeamInfo, teamInfo } from '@/api/market'
import { useMarketStore } from '@/stores/useMarketStore'
import type { AnyObj } from '@/types/common'
import { MARKET_USER_OWNER } from '@/views/Home/components/TeamMarket/config/market'

export function useBaseInfo() {
  const marketStore = useMarketStore()
  const inputRef = ref(null)
  const baseInfoData: any = ref({} as AnyObj)
  const leaveTemaConfig = {
    key: 'leaveTeam',
    label: 'leaveTeam',
    canEdit: false,
    type: 'button',
    hasToolTip: true,
    tooltip: 'leaveTeamTip',
    isEditing: false,
    btnType: '',
    openModalType: '',
    show: () => {
      return true
    },
  }
  const disbandTeamConfig = {
    key: 'disbandTeam',
    label: 'disbandTeam',
    canEdit: false,
    type: 'button',
    btnType: 'default',
    hasToolTip: true,
    tooltip: 'disbandTeamTip',
    isEditing: false,
    openModalType: '',
    show: (userType) => {
      return userType === MARKET_USER_OWNER
    },
  }
  const teamMarketConfig = ref([
    {
      key: 'marketName',
      label: 'marketName',
      canEdit: true,
      type: 'input',
      hasToolTip: true,
      isEditing: false,
    },
    {
      key: 'userName',
      label: 'creator',
      canEdit: false,
      type: 'label',
      hasToolTip: false,
      isEditing: false,
    },
    {
      key: 'createTime',
      label: 'created',
      canEdit: false,
      type: 'label',
      hasToolTip: false,
      isEditing: false,
    },
    {
      key: 'marketDescribe',
      label: 'marketDesc',
      canEdit: true,
      type: 'input',
      hasToolTip: true,
      isEditing: false,
    },
    {
      type: 'buttons',
      key: 'buttons',
      canEdit: true,
      label: 'input',
      hasToolTip: true,
      isEditing: false,
      list: [leaveTemaConfig, disbandTeamConfig],
    },
  ])

  const { isOnlyUser } = inject('isOnlyUser') as { isOnlyUser: Ref<boolean> }

  const editMarket = (itemConf) => {
    const { marketName, marketDescribe, marketId } = baseInfoData.value
    editTeamInfo({ marketName, marketDescribe, marketId })
      .then((res) => {
        if (res.data) {
          message.success('修改成功')
          marketStore.refreshTeamList('', true)
        }
        else {
          message.error('修改失败')
          baseInfoData.value.marketName = marketStore.activeMarket.marketName
        }
      })
      .catch(() => {
        baseInfoData.value.marketName = marketStore.activeMarket.marketName
      })
    itemConf.isEditing = false
  }

  const getTeamInfo = (id) => {
    teamInfo({ marketId: id }).then((res: any) => {
      baseInfoData.value = {
        ...res.data,
        marketId: id,
      }
    })
  }

  watch(() => marketStore.activeMarket?.marketId, (newVal) => {
    if (newVal) {
      getTeamInfo(newVal)
    }
  }, {
    immediate: true,
  })

  watch(() => marketStore.activeMarket?.userType, (newVal) => {
    if (newVal) {
      getTeamInfo(marketStore.activeMarket?.marketId)
    }
  })

  watch(() => isOnlyUser.value, (val) => {
    teamMarketConfig.value.forEach((item) => {
      if (item.key === 'buttons') {
        item.list = val ? [disbandTeamConfig] : [leaveTemaConfig, disbandTeamConfig]
      }
    })
  }, {
    immediate: true,
  })

  const setEditing = (item) => {
    item.isEditing = true
    nextTick(() => {
      inputRef.value[0].focus()
    })
  }

  return {
    teamMarketConfig,
    baseInfoData,
    inputRef,
    editMarket,
    setEditing,
  }
}
