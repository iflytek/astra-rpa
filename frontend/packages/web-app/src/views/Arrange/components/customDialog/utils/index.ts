import { cloneDeep } from 'lodash-es'

import {
  defaultFilePathConfig,
  defaultMultiSelectConfig,
  defaultSingleSelectConfig,
  defaultValueConfig,
  directionConfig,
  fileFilterConfig,
  fileTypeConfig,
  fontFamilyConfig,
  fontSizeConfig,
  fontStyleConfig,
  optionsConfig,
  pwdDefaultValueConfig,
  requiredConfig,
  textContentConfig,
  timeDefaultValueConfig,
  timeFormatConfig,
} from '../config/index.ts'
import type { FormItemConfig } from '../types'

function getLabelConfig(dialogFormName) {
  return {
    formType: {
      type: 'INPUT',
    },
    title: `${dialogFormName}标题`,
    default: 'dialogFormName',
    value: [
      {
        type: 'other',
        value: dialogFormName,
      },
    ],
    rpa: 'special',
    required: true,
  }
}
function getPlaceholderConfig(defaultPlaceholder) { // 输入框、密码框、文件选择、单选多选下拉框
  return {
    formType: {
      type: 'INPUT',
    },
    key: 'placeholder',
    title: '空白提示',
    placeholder: '请输入空白提示',
    default: defaultPlaceholder,
    value: [
      {
        type: 'other',
        value: defaultPlaceholder,
      },
    ],
    rpa: 'special',
  }
}
function getBindConfig(bindKey) {
  return {
    formType: {
      type: 'INPUT',
      params: {
        values: [
          'string',
        ],
      },
    },
    title: '输出变量名称',
    key: bindKey,
    value: [
      {
        type: 'str',
        value: `${bindKey}_1`,
      },
    ],
    rpa: 'special',
  }
}

// 对话框支持的表单配置
export const dialogFormConfig: Array<FormItemConfig> = [
  {
    id: '1',
    dialogFormType: 'INPUT',
    dialogFormName: '输入框',
    // configKeys: ['label', 'placeholder', 'defaultValue', 'bind', 'required', 'mockField'],
    configKeys: ['label', 'placeholder', 'defaultValue', 'bind', 'required'],
    label: getLabelConfig('输入框'),
    placeholder: getPlaceholderConfig('请输入文本内容'),
    defaultValue: defaultValueConfig,
    bind: getBindConfig('input_box'),
    required: requiredConfig,
    // mockField: {
    //   types: 'Str',
    //   formType: {
    //     type: 'SCRIPTPARAMS',
    //   },
    //   key: 'params',
    //   name: 'params',
    //   title: '参数管理',
    //   tip: '输入脚本相关的参数管理',
    //   value: '[]',
    //   required: true,
    // },
    // mockField: {
    //   types: 'Any',
    //   formType: {
    //     type: 'CONTENTPASTE',
    //   },
    //   key: 'email_body',
    //   title: '正文',
    //   name: 'email_body',
    //   tip: '正文相关tip',
    //   required: true,
    //   value: [
    //     {
    //       type: 'other',
    //       value: '',
    //     },
    //   ],
    // },
    // mockField: {
    //   types: 'Any',
    //   formType: {
    //     type: 'MODALBUTTON',
    //   },
    //   key: 'replace_text',
    //   title: '替换文字',
    //   name: 'replace_text',
    //   tip: '',
    //   required: false,
    //   value: '',
    // },
    // mockField: {
    //   types: 'Any',
    //   formType: {
    //     type: 'MOUSEPOSITION',
    //   },
    //   key: 'mouse_position',
    //   title: '获取坐标位置',
    //   name: 'mouse_position',
    //   tip: '',
    //   required: false,
    //   value: '',
    // },
  },
  {
    id: '2',
    dialogFormType: 'PASSWORD',
    dialogFormName: '密码框',
    configKeys: ['label', 'placeholder', 'defaultValue', 'bind', 'required'],
    label: getLabelConfig('密码框'),
    placeholder: getPlaceholderConfig('请输入密码'),
    defaultValue: pwdDefaultValueConfig,
    bind: getBindConfig('password_box'),
    required: requiredConfig,
  },
  {
    id: '3',
    dialogFormType: 'DATEPICKER',
    dialogFormName: '日期时间',
    configKeys: ['label', 'format', 'defaultValue', 'bind', 'required'],
    label: getLabelConfig('日期时间'),
    format: timeFormatConfig,
    defaultValue: timeDefaultValueConfig,
    bind: getBindConfig('datepicker_box'),
    required: requiredConfig,
    conditionalFnKey: 'DATEPICKER_LINK',
  },
  {
    id: '4',
    dialogFormType: 'PATH_INPUT',
    dialogFormName: '文件选择',
    configKeys: ['label', 'selectType', 'filter', 'placeholder', 'defaultPath', 'bind', 'required'],
    label: getLabelConfig('文件选择'),
    selectType: fileTypeConfig,
    filter: fileFilterConfig,
    placeholder: getPlaceholderConfig('请选择文件'),
    defaultPath: defaultFilePathConfig,
    bind: getBindConfig('path_input_box'),
    required: requiredConfig,
    conditionalFnKey: 'PATH_INPUT_LINK',
  },
  {
    id: '5',
    dialogFormType: 'RADIO_GROUP',
    dialogFormName: '单选框',
    configKeys: ['label', 'options', 'defaultValue', 'direction', 'bind', 'required'],
    label: getLabelConfig('单选框'),
    options: optionsConfig,
    defaultValue: defaultSingleSelectConfig,
    direction: directionConfig,
    bind: getBindConfig('radio_box'),
    required: requiredConfig,
    conditionalFnKey: 'OPTIONS_SINGLE_LINK',
  },
  {
    id: '6',
    dialogFormType: 'CHECKBOX_GROUP',
    dialogFormName: '复选框',
    configKeys: ['label', 'options', 'defaultValue', 'direction', 'bind', 'required'],
    label: getLabelConfig('复选框'),
    options: optionsConfig,
    defaultValue: defaultMultiSelectConfig,
    direction: directionConfig,
    bind: getBindConfig('check_box'),
    required: requiredConfig,
    conditionalFnKey: 'OPTIONS_MULTI_LINK',
  },
  {
    id: '7',
    dialogFormType: 'SINGLE_SELECT',
    dialogFormName: '单选下拉框',
    configKeys: ['label', 'options', 'placeholder', 'defaultValue', 'bind', 'required'],
    label: getLabelConfig('单选下拉框'),
    options: optionsConfig,
    placeholder: getPlaceholderConfig('请选择一项'),
    defaultValue: defaultSingleSelectConfig,
    bind: getBindConfig('single_select_box'),
    required: requiredConfig,
    conditionalFnKey: 'OPTIONS_SINGLE_LINK',
  },
  {
    id: '8',
    dialogFormType: 'MULTI_SELECT',
    dialogFormName: '多选下拉框',
    configKeys: ['label', 'options', 'placeholder', 'defaultValue', 'bind', 'required'],
    label: getLabelConfig('多选下拉框'),
    options: optionsConfig,
    placeholder: getPlaceholderConfig('请选择一项或多项'),
    defaultValue: defaultMultiSelectConfig,
    bind: getBindConfig('multi_select_box'),
    required: requiredConfig,
    conditionalFnKey: 'OPTIONS_MULTI_LINK',
  },
  {
    id: '9',
    dialogFormType: 'TEXT_DESC',
    dialogFormName: '文本',
    configKeys: ['fontFamily', 'fontSize', 'fontStyle', 'textContent'],
    fontFamily: fontFamilyConfig,
    fontSize: fontSizeConfig,
    fontStyle: fontStyleConfig,
    textContent: textContentConfig,
  },
]

// 联动处理函数
export const conditionalFn = {
  DATEPICKER_LINK(selectedItem) {
    const { format } = selectedItem
    selectedItem.defaultValue.formType.params.format = format.value
    return selectedItem
  },
  PATH_INPUT_LINK(selectedItem) {
    const { selectType } = selectedItem
    if (selectType.value === 'file') {
      selectedItem.configKeys = ['label', 'selectType', 'filter', 'placeholder', 'defaultPath', 'bind', 'required']
      selectedItem.filter = fileFilterConfig
      selectedItem.label = getLabelConfig('文件选择')
      selectedItem.placeholder = getPlaceholderConfig('请选择文件')
    }
    else {
      selectedItem.configKeys = ['label', 'selectType', 'placeholder', 'defaultPath', 'bind', 'required']
      delete selectedItem.filter
      selectedItem.label = getLabelConfig('文件夹选择')
      selectedItem.placeholder = getPlaceholderConfig('请选择文件夹')
    }
    return selectedItem
  },
  OPTIONS_SINGLE_LINK(selectedItem) {
    selectedItem.defaultValue.options = cloneDeep(selectedItem.options.value)
    const index = selectedItem.defaultValue.options.findIndex(i => i.rId === selectedItem.defaultValue.value)
    if (index === -1) {
      selectedItem.defaultValue.allowReverse = true
      selectedItem.defaultValue.value = ''
    }
    return selectedItem
  },
  OPTIONS_MULTI_LINK(selectedItem) {
    selectedItem.defaultValue.options = cloneDeep(selectedItem.options.value)
    selectedItem.defaultValue.allowReverse = true
    selectedItem.defaultValue.value = selectedItem.defaultValue.value.filter(i => selectedItem.defaultValue.options.some(j => j.rId === i))
    return selectedItem
  },
}

// 转换成表单弹窗所需的数据
export function transDataForPreview(dialogData) { // 自定义对话框预览所需要的数据转换
  const formModel = { result_button: 'confirm' }
  const itemList = dialogData?.formList.map((item) => {
    const { configKeys } = item
    const res = { dialogFormType: item.dialogFormType } as FormItemConfig
    configKeys.forEach((key) => {
      if (key === 'options') { // 选项组件特殊处理
        res[key] = item.options.value
      }
      else if (key === 'defaultPath') { // 文件夹默认值支持变量引入所以不支持预览
        res[key] = ''
      }
      else {
        res[key] = Array.isArray(item[key]?.value) && !['fontStyle', 'defaultValue'].includes(key) ? item[key]?.value[0]?.value : item[key]?.value
      }
    })
    if (item.dialogFormType !== 'TEXT_DESC') {
      formModel[res.bind] = res?.defaultValue
    }
    return JSON.parse(JSON.stringify(res)) // 去掉值为undefined的字段
  })
  return {
    itemList,
    formModel,
  }
}

// 计算得到正确的bindKey的Index
export function getRightIndex(dialogDataArr: FormItemConfig[], bindKey: string) {
  const filterArr = dialogDataArr?.filter(i => i.bind && i.bind.value[0].value.includes(bindKey))
  if (!filterArr.length)
    return 1
  return Number(filterArr
    .map(item => item.bind.value[0].value.replace(`${bindKey}_`, ''))
    .filter(i => /^\d*$/.test(i))
    .sort((a, b) => b - a)[0]) + 1
}
