import { Button, message } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import { isEmpty } from 'lodash-es'
import { onMounted, ref } from 'vue'

import { utilsManager, windowManager } from '@/platform'
import type { AnyObj } from '@/types/common'
import type { DialogOption, FormItemConfig } from '@/views/Arrange/components/customDialog/types'

const PICKER_MIN_HEIGHT = 340
const OTHER_MIN_HEIGHT = 200

export default function useUserFormDialog(props, emit) {
  // 定义表单引用
  const formRef = ref(null)
  // 定义对话框表单选项
  const optionData = ref({} as DialogOption)
  // 定义表单状态
  const formState = ref({} as AnyObj)
  // 保存标准输入内容
  const stdInputStr = ref('')
  const dialogType = ref('') // basic:基础对话框窗口 custom:自定义对话框窗口

  const getPasswordRules = (title: string) => (
    [
      {
        validator: (_rule: Rule, value: string) => {
          if (value.length < 4 || value.length > 16) {
            // eslint-disable-next-line prefer-promise-reject-errors
            return Promise.reject(`${title}请输入4-16位字符`)
          }
          return Promise.resolve()
        },
        trigger: 'change',
      },
    ]
  )

  // 定义基础对话框数据转换方法
  const transformBasic = (data: AnyObj): DialogOption => {
    // 获取用户表单选项
    function getUserFormOption(data) {
      let rules = null
      switch (data.key) {
        case 'Dialog.select_box':
          return {
            dialogFormType: data.select_type === 'multi' ? 'MULTI_SELECT' : 'SINGLE_SELECT',
            label: data.options_title,
            options: data?.options?.map((op) => {
              return {
                label: op.value,
                value: op.value,
              }
            }) || [],
            defaultValue: data.select_type === 'multi' ? [] : '',
          }
        case 'Dialog.input_box':
          if (data.input_type !== 'text') {
            rules = getPasswordRules(data.input_title)
          }
          return {
            dialogFormType: data.input_type === 'text' ? 'INPUT' : 'PASSWORD',
            label: data.input_title,
            defaultValue: data.default_input,
            rules,
          }
        case 'Dialog.select_time_box':
          return {
            dialogFormType: data.time_type === 'time' ? 'DATEPICKER' : 'RANGERPICKER',
            label: data.input_title,
            format: data.time_format,
            defaultValue: data.time_type === 'time' ? data.default_time : data.default_time_range,
          }
        case 'Dialog.select_file_box':
          return {
            dialogFormType: 'PATH_INPUT',
            label: data.select_title,
            defaultPath: data.default_path,
            selectType: data.open_type,
            filter: data.file_type,
            isMultiple: data.multiple_choice,
            // defaultValue: data.open_type === 'folder' ? data.default_path : '',
          }
        case 'Dialog.message_box':
          return {
            dialogFormType: 'MESSAGE_CONTENT',
            messageType: data.message_type,
            messageContent: data.message_content,
            defaultValue: data?.default_button || data?.default_button_c || data?.default_button_cn || data?.default_button_y || data?.default_button_yn,
          }
        default:
          break
      }
    }
    const temp = getUserFormOption(data)
    return {
      mode: 'window',
      title: data.box_title || data.box_title_file || data.box_title_folder,
      buttonType: data?.button_type || 'confirm_cancel',
      itemList: [{
        bind: data.outputkey,
        ...temp,
      }],
      formModel: {
        [data.outputkey]: temp?.defaultValue || '',
      },
    }
  }
  // 定义自定义对话框数据转换方法
  const transformCustom = (data: string): DialogOption => {
    const { box_title, design_interface, result_button } = JSON.parse(data || '{}')
    console.log('design_interface', design_interface)
    const { mode = 'window', buttonType = 'confirm_cancel', formList = [] } = JSON.parse(design_interface || '{}')
    console.log('formList', formList)
    const formModel = { result_button } as AnyObj
    const itemList = formList?.map((item) => {
      const { configKeys, dialogFormType } = item
      const res = { dialogFormType } as FormItemConfig
      configKeys.forEach((key) => {
        if (key === 'options') {
          res[key] = item[key].value?.map((op) => {
            // const { rId, value } = op
            return {
              label: op.value,
              value: op.value,
            }
          })
        }
        else {
          // eslint-disable-next-line no-prototype-builtins
          res[key] = item[key]?.hasOwnProperty('value') ? item[key]?.value : item[key]
        }
      })
      if (configKeys.includes('options') && configKeys.includes('defaultValue')) {
        res.defaultValue = item.options.value.find(op => op.rId === res.defaultValue)?.value || item.defaultValue.defualt
      }
      if (dialogFormType !== 'TEXT_DESC') {
        formModel[res.bind] = res?.defaultValue || res?.defaultPath
      }
      const result = JSON.parse(JSON.stringify(res)) // 过滤掉值为undefined的字段
      if (dialogFormType === 'PASSWORD') { // 密码框统一加上长度校验
        result.rules = getPasswordRules(result.label)
      }
      return result
    })
    return {
      mode,
      title: box_title || '自定义对话框',
      buttonType,
      itemList,
      formModel,
    }
  }
  function initOptionData() { // 初始化信息
    console.log('created useUserFormDialog2')
    if (props?.option && !isEmpty(props?.option)) { // 来自于预览弹窗
      optionData.value = props.option
    }
    else { // 来自于运行窗口
      const targetInfo = new URL(location.href).searchParams
      const windowOption = targetInfo.get('option')
      console.log('windowOption+++++++++++++++', windowOption)
      if (windowOption) { // 来自于基础对话框的运行窗口
        dialogType.value = 'basic'
        optionData.value = transformBasic(JSON.parse(windowOption)) as DialogOption
        // 如果包含日期控件最小高度需要调整
        const hasDatePicker = optionData.value.itemList.some(item => ['DATEPICKER', 'RANGERPICKER'].includes(item.dialogFormType))
        if (hasDatePicker) {
          setTimeout(async () => {
            const { offsetWidth: bodyWidth } = document.body
            await windowManager.setWindowSize({ width: bodyWidth, height: PICKER_MIN_HEIGHT })
            await windowManager.centerWindow()
          }, 500)
        }
      }
      else {
        dialogType.value = 'custom'
        // 来自于自定义对话框的运行窗口另做处理，详见listen_to_stdin
      }
    }
    formState.value = optionData.value.formModel || {}
  }
  console.log('created useUserFormDialog1')
  initOptionData()
  console.log('created useUserFormDialog3')
  const closeWindowFormDialog = () => windowManager.closeWindow()

  const handleClose = () => {
    if (optionData.value.mode === 'modal') {
      emit('close')
      return
    }
    // 自定义对话框点击×关闭时才需要输出{ result_button: 'cancel' }
    dialogType.value === 'custom' ? saveData({ result_button: 'cancel' }) : closeWindowFormDialog()
  }
  const saveData = (data: AnyObj) => {
    console.log('saveData', data)
    utilsManager.invoke('page_handler', {
      operType: 'UserForm',
      data: JSON.stringify(data),
    }).then(() => {
      closeWindowFormDialog()
    })
  }
  const handleBtns = (btnOpt: string) => {
    if (optionData.value.mode === 'modal') { // 只要是预览弹窗没有任何业务逻辑直接关闭
      emit('close')
      return
    }
    if (optionData.value.itemList.length === 1 && optionData.value.itemList[0].dialogFormType === 'MESSAGE_CONTENT') {
      formState.value[optionData.value.itemList[0].bind] = btnOpt
      saveData(formState.value)
    }
    else {
      if (btnOpt === 'confirm') {
        formRef.value.validate().then(() => {
          formState.value.result_button = btnOpt
          saveData(formState.value)
        }).catch(() => {
          message.warning('请检查表单内容')
        })
      }
      if (btnOpt === 'cancel') {
        saveData({
          result_button: 'cancel',
        })
      }
    }
  }
  const renderFooterBtns = (buttonType: string) => {
    switch (buttonType) {
      case 'confirm':
        return (<Button type="primary" onClick={() => { handleBtns('confirm') }}>确定</Button>)
      case 'confirm_cancel':
        return (
          <>
            <Button onClick={() => { handleBtns('cancel') }}>取消</Button>
            <Button type="primary" onClick={() => { handleBtns('confirm') }}>确定</Button>
          </>
        )
      case 'yes_no':
        return (
          <>
            <Button onClick={() => { handleBtns('no') }}>否</Button>
            <Button type="primary" onClick={() => { handleBtns('yes') }}>是</Button>
          </>
        )
      case 'yes_no_cancel':
        return (
          <>
            <Button onClick={() => { handleBtns('cancel') }}>取消</Button>
            <Button onClick={() => { handleBtns('no') }}>否</Button>
            <Button type="primary" onClick={() => { handleBtns('yes') }}>是</Button>
          </>
        )
      default:
        return (<Button type="primary">确定</Button>)
    }
  }

  const resizeWindow = (minWinHeight: number) => {
    // 计算设置自定义对话框窗口高度，实现高度随动
    const { offsetWidth: bodyWidth } = document.body
    const userHeaderHeight = (document.querySelector('.userform-header') as HTMLElement)?.offsetHeight
    const userFooterHeight = (document.querySelector('.userform-footer') as HTMLElement)?.offsetHeight
    const formHeight = document.forms[0].offsetHeight
    let resHeight = formHeight + userHeaderHeight + userFooterHeight + 65
    // 判断计算高度是否超过了所在屏幕高度
    windowManager.getScreenWorkArea().then(async (screenWorkArea) => {
      if (resHeight < minWinHeight) {
        resHeight = minWinHeight
      }
      if (resHeight > screenWorkArea.height) {
        resHeight = screenWorkArea.height
      }
      await windowManager.setWindowSize({ width: bodyWidth, height: resHeight })
      await windowManager.centerWindow()
      utilsManager.invoke('page_handler', {
        operType: 'UserForm',
        data: 'noresize',
      })
    })
  }

  utilsManager.listenEvent('listen_to_stdin', (eventMsg) => {
    console.log('listen_to_stdin', eventMsg)
    if (eventMsg.includes('option_start')) {
      stdInputStr.value = ''
      return
    }
    if (eventMsg.includes('option_end')) {
      optionData.value = transformCustom(stdInputStr.value) as DialogOption
      console.log('optionData', optionData.value)
      formState.value = optionData.value.formModel || {}
      setTimeout(() => {
        // 如果包含日期控件最小高度需要调整
        const hasDatePicker = optionData.value.itemList.some(item => ['DATEPICKER', 'RANGERPICKER'].includes(item.dialogFormType))
        const minWinHeight = hasDatePicker ? PICKER_MIN_HEIGHT : OTHER_MIN_HEIGHT
        resizeWindow(minWinHeight)
      })
      return
    }
    stdInputStr.value += eventMsg
  })

  onMounted(() => {
    console.log('onMounted userFormDialog')
    dialogType.value === 'custom' && utilsManager.invoke('listen_to_stdin', {})
  })

  return {
    formRef,
    dialogType,
    optionData,
    formState,
    handleClose,
    renderFooterBtns,
  }
}
