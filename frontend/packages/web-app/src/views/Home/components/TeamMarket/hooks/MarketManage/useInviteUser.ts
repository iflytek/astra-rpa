import { message } from 'ant-design-vue'
import { debounce } from 'lodash-es'
import { ref } from 'vue'

import { /* TODO 暂时注释掉， 后续组织架构功能完善再打开 getCompanyInfo, */ getInviteUser, getTransferUser } from '@/api/market'
import { MARKET_USER_ADMIN } from '@/views/Home/components/TeamMarket/config/market'
import type { resOption } from '@/views/Home/types'

export function usePhoneInvite(marketId: string, type: string = 'invite', emit?: any) {
  const userList = ref([])
  const phoneInviteArr = ref([])

  const userListByPhone = debounce((phone) => {
    if (!phone) {
      userList.value = []
      return
    }

    if (Object.is(Number(phone), Number.NaN) || phone.length > 11) {
      message.destroy()
      message.error('请输入正确的手机号')
      userList.value = []
      return
    }

    const func = type === 'invite' ? getInviteUser : getTransferUser
    func({ phone, marketId }).then((res: resOption) => {
      const { data } = res
      if (Array.isArray(data)) {
        userList.value = data.map((item) => {
          if (!item.userType)
            item.userType = MARKET_USER_ADMIN
          return item
        })
      }
    })
  }, 200)

  const keyDownChange = (e) => {
    const { keyCode } = e
    if (keyCode === 13 && userList.value.length === 1) {
      const id = userList.value[0].creatorId
      if (!phoneInviteArr.value.includes(id)) {
        phoneInviteArr.value.push(id)
        triggerChange()
      }
    }
  }

  const selectData = (val) => {
    phoneInviteArr.value = val
    triggerChange()
  }

  const triggerChange = () => {
    const selectUsers = userList.value.filter(i => phoneInviteArr.value.includes(i.creatorId))
    const users = selectUsers.map((item) => {
      return {
        userType: item.userType,
        creatorId: item.creatorId,
      }
    })
    emit && emit('change', users)
  }
  const changePhoneUserType = (item, userType) => {
    item.userType = userType
  }
  const clearUserList = () => {
    userList.value = []
  }

  const resetPhoneInviteArr = () => {
    phoneInviteArr.value = []
    triggerChange()
  }
  return {
    userList,
    userListByPhone,
    phoneInviteArr,
    clearUserList,
    keyDownChange,
    selectData,
    changePhoneUserType,
    resetPhoneInviteArr,
  }
}

export function useCompanyInvite(marketId: string, emit: any) {
  const companyTreeData = ref([])
  const companyInviteArr = ref([])

  // TODO 暂时注释掉， 后续组织架构功能完善再打开
  // const getCompanyData = () => {
  //   getCompanyInfo({ marketId }).then((res: resOption) => {
  //     const { data } = res
  //     // 遍历添加userType字段
  //     const dataDFS = (treeData) => {
  //       return treeData.map((node) => {
  //         const { type, children } = node
  //         if (children?.length) {
  //           node.children = dataDFS(children)
  //         }
  //         else {
  //           type === 'user' && (node.userType = MARKET_USER_ADMIN)
  //         }
  //         return node
  //       })
  //     }
  //     if (Array.isArray(data)) {
  //       companyTreeData.value = dataDFS(data)
  //     }
  //   })
  // }

  const changeCompanyUserType = (item, userType) => {
    item.data.userType = userType
  }

  const triggerChange = () => {
    const inviteArr = []
    const loopTreeData = (treeData) => {
      if (!treeData)
        return false
      treeData.forEach((node) => {
        if (node.children) {
          const { children } = node
          children && children.length > 0 && loopTreeData(children)
        }
        else {
          node.userType && companyInviteArr.value.includes(node.deptOrUserId) && inviteArr.push({
            creatorId: Number(node.deptOrUserId),
            userType: node.userType,
          })
        }
      })
    }

    loopTreeData(companyTreeData.value)
    emit('change', inviteArr)
  }

  const changeCompanySelect = () => {
    triggerChange()
  }

  const resetCompanyInviteArr = () => {
    companyInviteArr.value = []
    triggerChange()
  }

  // TODO 暂时注释掉， 后续组织架构功能完善再打开
  // getCompanyData()
  return {
    companyTreeData,
    companyInviteArr,
    changeCompanySelect,
    changeCompanyUserType,
    resetCompanyInviteArr,
  }
}
