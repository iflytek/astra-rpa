import { message } from 'ant-design-vue'
// 元素信息
import { defineStore } from 'pinia'
import type { Ref } from 'vue'
import { ref } from 'vue'

import { addBase64Header, base64ToFile } from '@/utils/common'
import BUS from '@/utils/eventBus'

import { addElement, addElementGroup, delElementGroup, generateCvElementName, getElementDetail, getElementsAll, moveElement, postDeleteElement, renameElementGroup, updateElement, uploadFile } from '@/api/resource'
import { useProcessStore } from '@/stores/useProcessStore'
import type { Element, ElementGroup, PickStepType } from '@/types/resource.d'
import { useGlobalDataUpdate } from '@/views/Arrange/hook/useGlobalDataUpdate'
import { gainUnUseQuote } from '@/views/Arrange/hook/useQuoteManage'

export const useCvStore = defineStore('cv', () => {
  const processStore = useProcessStore()
  const cvTreeData = ref<ElementGroup[]>([])
  const currentCvItem = ref<Element | null>(null)
  let isNewElement = false
  const { elementDeleteAndUpdateFlow, elementRenameAndUpdateFlow } = useGlobalDataUpdate()

  // 获取cv拾取数据
  const getCvTreeData = async () => {
    getElementsAll({ robotId: processStore.project.id, elementType: 'cv' }).then((res: any) => {
      cvTreeData.value = res.data.map((i) => {
        if (i.open === undefined)
          i.open = true
        return i
      })
    })
  }

  // 新增分组
  const addGroup = (groupName: string) => {
    return new Promise((resolve, reject) => {
      addElementGroup({ robotId: processStore.project.id, groupName, elementType: 'cv' }).then((res) => {
        console.log(res)
        message.success('新增成功')
        updateCvTreeData()
        resolve(true)
      }).catch((err) => {
        reject(err)
      })
    })
  }

  // 分组重命名
  const renameGroup = (groupId: string, groupName: string) => {
    return new Promise((resolve, reject) => {
      renameElementGroup({ robotId: processStore.project.id, groupId, groupName, elementType: 'cv' }).then((res) => {
        console.log(res)
        message.success('重命名成功')
        updateCvTreeData()
        resolve(true)
      }).catch((err) => {
        reject(err)
      })
    })
  }

  // 删除分组
  const deleteGroup = (groupId: string) => {
    const delElments = cvTreeData.value.find(i => i.id === groupId).elements
    delElementGroup({ robotId: processStore.project.id, groupId }).then(() => {
      message.success('删除成功')
      updateCvTreeData()
      // 更新流程数据-删除该分组下的图像
      elementDeleteAndUpdateFlow({ elementIds: delElments.map(i => i.id) })
    })
  }

  // 更新分组
  const updateCvTreeData = () => {
    getCvTreeData()
  }

  const getCvItemDetail = async (elementId: string) => {
    const { data } = await getElementDetail({ robotId: processStore.project.id, elementId })
    isNewElement = false
    return data
  }

  const uploadImgFile = async () => {
    if (isNewElement) {
      const { id, imageUrl, parentImageUrl } = currentCvItem.value
      const fileName = `${id}.png`
      const [imageId, parentImageId] = await Promise.all([
        imageUrl ? uploadFile({ file: base64ToFile(imageUrl, fileName) }) : Promise.resolve(''),
        parentImageUrl ? uploadFile({ file: base64ToFile(parentImageUrl, `parent_${fileName}`) }) : Promise.resolve(''),
      ])
      return { imageId, parentImageId }
    }
    return {}
  }

  // 保存图像
  const saveCvItem = async (cvParams: Element, groupId: string = '') => {
    return new Promise((resolve, reject) => {
      const robotId = processStore.project.id
      const _name = cvParams.name.replaceAll(' ', '') // 去除空格
      if (_name === '') {
        reject(new Error('请输入元素名称'))
      }

      uploadImgFile().then((res: any) => {
        const params = {
          robotId,
          groupName: groupId ? cvTreeData.value.find(i => i.id === groupId)?.name : '',
          element: {
            ...cvParams,
            name: _name,
            ...res,
          },
          type: 'cv',
        }
        // 拾取
        const id = cvParams.id && isCVItemExsist(cvParams.id) ? cvParams.id : ''
        const reqFunc = id ? updateElement : addElement
        reqFunc(params).then((res) => {
          BUS.$emit('cv-pick-done', { data: id || res.data.elementId, value: _name }) // 通知其他组件拾取已完成
          updateCvTreeData() // 更新树形数据
          if (id && currentCvItem.value?.name !== _name) { // 名称有变化, 修改流程数据中的名称
            elementRenameAndUpdateFlow({ elementId: id, name: _name })
          }
          resolve(true)
        }).catch((err) => {
          reject(err)
        })
      })
    })
  }

  // 删除图像
  const deleteCvItem = (cvItem: Element) => {
    postDeleteElement({ robotId: processStore.project.id, elementId: cvItem.id }).then((res) => {
      console.log(res)
      updateCvTreeData()
      // 更新流程数据-删除该图像
      elementDeleteAndUpdateFlow({ elementIds: [cvItem.id] })
    })
  }
  // 移动图像到某个分组
  const moveCvItem = (id: string, groupId: string) => {
    moveElement({ robotId: processStore.project.id, groupId, elementId: id }).then((res) => {
      console.log(res)
      updateCvTreeData()
    })
  }

  const setCurrentCvItem = (cvItem: Element) => {
    isNewElement = false
    currentCvItem.value = cvItem
  }

  // 设置临时图像
  const setTempCvItem = async (data: any, pickStep: PickStepType = 'new') => {
    let element: Element
    const { img } = data
    const imageUrl = img.self ? addBase64Header(img.self) : ''
    const parentImageUrl = img.parent ? addBase64Header(img.parent) : ''
    const elementData = {
      ...data,
      img: {
        // cv图片, 存储后则为图片地址
        self: '',
        parent: '',
      },
      defaultAnchor: pickStep !== 'anchor',
    }

    if (pickStep === 'new') {
      // 新建元素，name、elementId, img 需要生成
      // const name = generateName(`图像_1`)
      const data = await generateCvElementName({ robotId: processStore.project.id })
      const name = data.data
      // const elementId = genNonDuplicateID('cv')
      element = {
        name,
        // id: elementId,
        imageUrl,
        parentImageUrl,
        elementData,
      }
    }
    else if (pickStep === 'repick') {
      // 重新拾取元素，图片， elementData 需要替换
      element = { ...currentCvItem.value, imageUrl, parentImageUrl, elementData }
    }
    else if (pickStep === 'anchor') {
      // 锚点替换 currentElement.value.parentImageUrl, currentElement.value.elementData elementData中的pos需要替换
      const selfPos = JSON.parse(currentCvItem.value.elementData).pos
      elementData.pos = { ...data.pos, self_x: selfPos.self_x, self_y: selfPos.self_y }
      element = { ...currentCvItem.value, parentImageUrl, elementData }
    }
    element.elementData = JSON.stringify(elementData)
    setCurrentCvItem(element)
    isNewElement = true
  }

  const quotedItem = ref(null)

  const setQuotedItem = (item?: Element) => {
    quotedItem.value = item || null
  }

  const getUnUseTreeData = (unuseTreeData: Ref, unUseNum: Ref, type: string) => {
    gainUnUseQuote((useImageIds) => {
      unuseTreeData.value = cvTreeData.value.map((item) => {
        return {
          ...item,
          elements: item.elements.filter(i => !useImageIds.includes(i.id)),
        }
      }).filter(i => i.elements.length > 0)
      unUseNum.value = 0
      unuseTreeData.value.forEach((item) => {
        unUseNum.value += item.elements.length
      })
    }, type)
  }

  const isCVItemExsist = (id: string) => {
    return cvTreeData.value.some(i => i.elements.some(j => j.id === id))
  }

  const resetCurrentItem = () => {
    setCurrentCvItem(null)
    isNewElement = false
  }

  return {
    cvTreeData,
    getCvTreeData,
    updateCvTreeData,
    addGroup,
    renameGroup,
    deleteGroup,
    getCvItemDetail,
    saveCvItem,
    deleteCvItem,
    moveCvItem,
    currentCvItem,
    setCurrentCvItem,
    setTempCvItem,
    quotedItem,
    setQuotedItem,
    getUnUseTreeData,
    resetCurrentItem,
    isCVItemExsist,
  }
})
