import { useProcessStore } from '@/stores/useProcessStore'
import { useVariableStore } from '@/stores/useVariableStore'

export function getRealValue(itemValue, mark = '') {
  let res
  const totalArr = [...useVariableStore().globalVariableList, ...useProcessStore().parameters]
  Array.isArray(itemValue)
    ? res = itemValue.map((i) => {
      console.log(i)
      return i.type === 'var' ? (totalArr.find(v => v.varName === i.value)?.varValue || mark || i.value) : i.value
    }).join('')
    : res = itemValue
  return res
}

function getSelectBoxOption({ inputList }) {
  let title = ''
  let dialogFormType = ''
  let options = []
  let label = ''
  inputList.forEach((item) => {
    if (item.key === 'box_title') {
      title = getRealValue(item.value)
    }
    if (item.key === 'select_type') {
      dialogFormType = getRealValue(item.value) === 'multi' ? 'MULTI_SELECT' : 'SINGLE_SELECT'
    }
    if (item.key === 'options') {
      options = item.value
    }
    if (item.key === 'options_title') {
      label = getRealValue(item.value)
    }
  })
  return {
    title,
    itemList: [{
      dialogFormType,
      label,
      options,
    }],
  }
}
function getInputBoxOption({ inputList }) {
  let title = ''
  let dialogFormType = ''
  let label = ''
  let defaultValueTxt = ''
  let defaultValuePsd = ''
  inputList.forEach((item) => {
    if (item.key === 'box_title') {
      title = getRealValue(item.value)
    }
    if (item.key === 'input_type') {
      dialogFormType = getRealValue(item.value) === 'text' ? 'INPUT' : 'PASSWORD'
    }
    if (item.key === 'input_title') {
      label = getRealValue(item.value)
    }
    if (item.key === 'default_input_text') {
      defaultValueTxt = item.value
    }
    if (item.key === 'default_input_pwd') {
      defaultValuePsd = item.value
    }
  })
  return {
    title,
    itemList: [{
      dialogFormType,
      label,
      defaultValue: dialogFormType === 'INPUT' ? defaultValueTxt : defaultValuePsd,
    }],
  }
}
function getDateBoxOption({ inputList }) {
  let title = ''
  let dialogFormType = ''
  let label = ''
  let format = ''
  let default_time = ''
  let default_time_range = ''
  let defaultValue = ''
  inputList.forEach((item) => {
    if (item.key === 'box_title') {
      title = getRealValue(item.value)
    }
    if (item.key === 'time_type') {
      dialogFormType = getRealValue(item.value) === 'time' ? 'DATEPICKER' : 'RANGERPICKER'
    }
    if (item.key === 'time_format') {
      format = getRealValue(item.value)
    }
    if (item.key === 'default_time') {
      default_time = getRealValue(item.value)
    }
    if (item.key === 'default_time_range') {
      default_time_range = item.value
    }
    if (item.key === 'input_title') {
      label = getRealValue(item.value)
    }
  })
  defaultValue = dialogFormType === 'DATEPICKER' ? default_time : default_time_range
  return {
    title,
    itemList: [{
      dialogFormType,
      label,
      format,
      defaultValue,
    }],
  }
}
function getPathBoxOption({ inputList }) {
  let title = ''
  let file_title = ''
  let folder_title = ''
  let label = ''
  let selectType = ''
  let filter = ''
  let isMultiple = true
  inputList.forEach((item) => {
    if (item.key === 'box_title_file') {
      file_title = getRealValue(item.value)
    }
    if (item.key === 'box_title_folder') {
      folder_title = getRealValue(item.value)
    }
    if (item.key === 'open_type') {
      selectType = getRealValue(item.value)
    }
    if (item.key === 'file_type') {
      filter = getRealValue(item.value)
    }
    if (item.key === 'multiple_choice') {
      isMultiple = getRealValue(item.value)
    }
    if (item.key === 'select_title') {
      label = getRealValue(item.value)
    }
  })
  title = selectType === 'file' ? file_title : folder_title
  return {
    title,
    itemList: [{
      dialogFormType: 'PATH_INPUT',
      label,
      selectType,
      filter,
      isMultiple,
    }],
  }
}
function getMessageBoxOption({ inputList }) {
  let title = ''
  let messageType = ''
  let messageContent = ''
  let buttonType = ''
  inputList.forEach((item) => {
    if (item.key === 'box_title') {
      title = getRealValue(item.value)
    }
    if (item.key === 'message_type') {
      messageType = getRealValue(item.value)
    }
    if (item.key === 'message_content') {
      // messageContent = getRealValue(item.value)
      // messageContent = getMsgContent(item.value)
      messageContent = item.value
    }
    if (item.key === 'button_type') {
      buttonType = getRealValue(item.value)
    }
  })
  return {
    title,
    buttonType,
    itemList: [{
      dialogFormType: 'MESSAGE_CONTENT',
      messageType,
      messageContent,
    }],
  }
}
export function getUserFormOption({ key, inputList }) {
  switch (key) {
    case 'Dialog.select_box':
      return getSelectBoxOption({ inputList })
    case 'Dialog.input_box':
      return getInputBoxOption({ inputList })
    case 'Dialog.select_time_box':
      return getDateBoxOption({ inputList })
    case 'Dialog.select_file_box':
      return getPathBoxOption({ inputList })
    case 'Dialog.message_box':
      return getMessageBoxOption({ inputList })
    default:
      break
  }
}

function usePreview() { }

export default usePreview
