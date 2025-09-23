export const SUPPORTED_PROTOCOLS = ['http://', 'https://', 'file://', 'ftp://']

export const IGNORE_KEYS = ['getElement', 'backgroundInject', 'contentInject']

export const V2_EXTENSION_ID = 'dibfknoajiboamheempfppeapcedplgm'

export const V3_EXTENSION_ID = 'gfpcfabhkgenjcmjgnldmkhjieekeeea'

export const CURRENT_EXTENSION_ID = chrome.runtime.id

export enum StatusCode {
  SUCCESS = '0000',
  UNKNOWN_ERROR = '5001',
  ELEMENT_NOT_FOUND = '5002',
  EXECUTE_ERROR = '5003',
  VERSION_ERROR = '5004',
}

export enum ErrorMessage {
  TAB_GET_ERROR = '获取标签页失败',
  ACTIVE_TAB_ERROR = '未找到活动标签页',
  NUMBER_ID_ERROR = 'id 必须是数字',
  FRAME_GET_ERROR = '未找到元素对应的iframe',
  CURRENT_TAB_UNSUPPORT_ERROR = '当前标签页不支持web拾取协议',
  NOT_SIMILAR_ELEMENT = '该元素不是相似元素',
  SIMILAR_NOT_FOUND = '未找到相似元素',
  RELATIVE_ELEMENT_PARAMS_ERROR = '关联元素参数错误',
  ELEMENT_NOT_FOUND = '未找到元素',
  UNSUPPORT_ERROR = '暂未实现',
  PARAMS_URL_NOT_FOUND = '缺少url字段！',
  PARAMS_NAME_NOT_FOUND = '缺少name字段！',
  PARAMS_NAME_VALUE_NOT_FOUND = '缺少必填字段name, value！',
  CONTEXT_NOT_FOUND = '未找到执行上下文，请确保页面已加载完成',
  EXECUTE_ERROR = '执行失败，未获取到结果',
  DEBUGGER_TIMOUT = '检测 Debugger 状态超时',
}

export enum SuccessMessage {
  DELETE_SUCCESS = '删除成功',
  SET_SUCCESS = '设置成功',
}
