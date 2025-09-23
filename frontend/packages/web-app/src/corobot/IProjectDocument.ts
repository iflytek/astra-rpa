import type { Bus as Emittery } from '@/utils/eventBus'

import type { ProcessNode } from '@/corobot/type'

import type {
  ElementGroupVM,
  ElementVM,
  GlobalVariableVM,
  ProcessNodeVM,
  ProjectVM,
  PythonPackageVM,
} from './vm'

interface BaseEvent<T, U = undefined> {
  add: [index: number[], data: T | T[], options: U]
  delete: [index: number[], data: T | T[], options: U]
  update: [index: number[], data: T[], options: U]
  [key: string]: any
}

export interface ProcessEvent extends BaseEvent<ProcessNodeVM> {
  open: [processId: string, nodes: ProcessNodeVM[], type: string] // 打开/加载流程
  close: [processId: string] // 关闭流程
}

export interface ProcessNodeEvent
  extends BaseEvent<ProcessNodeVM, { processId: string }> {}

export interface ElementGroupEvent extends BaseEvent<ElementGroupVM> {}

export interface ElementEvent
  extends BaseEvent<ElementVM, { groupId: string }> {}

export interface GlobalVariableEvent extends BaseEvent<GlobalVariableVM> {}

export interface PythonPackageEvent extends BaseEvent<PythonPackageVM> {}

interface BaseActor<T, U = undefined> {
  add: (index: number[], data: T[], options: U) => void
  delete: (data: string[], options: U) => void
  update: (index: number[], data: T[], options: U) => void
  move: (from: number, to: number, options: U) => void
}

export interface ProcessActor {
  loadProcess: (processId: string) => Promise<void>
  saveProcess: (processId: string) => Promise<void>
  gainProcess: (processId: string) => ProcessNode[] | RPA.Atom[]
  addProcessOrModule: (type: RPA.Flow.ProcessModuleType, name: string) => Promise<string>
  copyProcessOrModule: (type: RPA.Flow.ProcessModuleType, name: string) => Promise<unknown>
  genProcessOrModuleName: (type: RPA.Flow.ProcessModuleType) => Promise<string>
  updateProcessOrModule: (type: RPA.Flow.ProcessModuleType, processId: string, name: string) => Promise<unknown>
  deleteProcessOrModule: (data: RPA.Flow.ProcessModule) => Promise<boolean>
}
export interface ProcessNodeActor
  extends BaseActor<ProcessNodeVM, { processId: string, conditionId?: any }> {
  canUndo: (processId: string) => boolean
  undo: (processId: string) => void
  canRestore: (processId: string) => boolean
  restore: (processId: string) => void
  clear: (processId: string) => void
  clearAll: () => void
}
export interface ElementGroupActor extends BaseActor<ElementGroupVM> {}
export interface ElementActor
  extends BaseActor<ElementVM, { groupId: string }> {}
export interface GlobalVariableActor extends BaseActor<GlobalVariableVM> {}
export interface PythonPackageActor extends BaseActor<PythonPackageVM> {}

/**
 * 把整个机器人工程当成一个文档，所有的操作都是对这个文档的操作
 * 操作文档后，文档数据的变更通过 emitter 回调给业务层
 * 业务层拿到回调的数据，更新 UI
 */
export interface IProjectDocument {
  readonly id: string
  // nodeAbilityMap: Record<string, Record<string, any>>
  // MAKR: 加载工程
  loadProject: () => Promise<ProjectVM>
  loadNodeAbilityList: (list: ProcessNodeVM[], processId: string, type: string) => void
  getProcessNodes: (processId: string) => ProcessNodeVM[]

  // MAKR: 通过 emitter 接收数据源的变动
  processEmitter: Emittery<ProcessEvent>
  processNodeEmitter: Emittery<ProcessNodeEvent>
  // 其他暂未实现
  elementGroupEmitter?: Emittery<ElementGroupEvent>
  elementEmitter?: Emittery<ElementEvent>
  globalVariableEmitter?: Emittery<GlobalVariableEvent>
  pythonPackageEmitter?: Emittery<PythonPackageEvent>

  // MAKR: 所有编辑操作的入口，业务层不直接操作数据源
  processActor: ProcessActor
  processNodeActor: ProcessNodeActor
  // 其他暂未实现
  elementGroupActor?: ElementGroupActor
  elementActor?: ElementActor
  globalVariableActor?: GlobalVariableActor
  pythonPackageActor?: PythonPackageActor
}
