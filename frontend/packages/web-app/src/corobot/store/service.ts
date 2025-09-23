import { getAbilityInfo, getNewAtomDesc, getTreeByParentKey } from '@/api/atom'
import { addProcess as addProcessApi, addProcessPyCode, copyProcess as copyProcessApi, copyProcessPyCode, deleteProcessPyCode, delProcess, flowSave, genProcessName as genProcessNameApi, genProcessPyCodeName, getProcess, getProcessAndCodeList, renameProcess as renameProcessApi, renameProcessPyCode } from '@/api/resource'
import type { ProcessNodeVM, ProjectVM } from '@/corobot/vm'

export function loadProject(robotId: string): Promise<ProjectVM> {
  return getProcessAndCodeList({ robotId }).then(res => ({
    id: robotId,
    name: '',
    processes: res,
    packages: [],
    global: [],
    env: [],
    elements: [],
    images: [],
  }))
}

export async function saveProject() {
  // 现有框架是分步保存的，不需要
}

export function loadProcess(_processId: string, _robotId: string): Promise<ProcessNodeVM[]> {
  return getProcess({ processId: _processId, robotId: _robotId }).then((res) => {
    return JSON.parse(res.data || '[]')
  })
}

export async function saveProcess(_processId: string, _robotId: string, _process: ProcessNodeVM[]) {
  return flowSave({ processId: _processId, robotId: _robotId, processJson: JSON.stringify(_process) })
}

export function addProcess(_robotId: string, _processName: string) {
  return addProcessApi({ robotId: _robotId, processName: _processName })
}

export function addModule(_robotId: string, _moduleName: string) {
  return addProcessPyCode({ robotId: _robotId, moduleName: _moduleName })
}
export function copyProcess(_robotId: string, _processId: string) {
  return copyProcessApi({ robotId: _robotId, processId: _processId })
}

export function copyModule(_robotId: string, _moduleId: string) {
  return copyProcessPyCode({ robotId: _robotId, moduleId: _moduleId })
}
export function genProcessName(_robotId: string) {
  return genProcessNameApi({ robotId: _robotId })
}

export function genModuleName(_robotId: string) {
  return genProcessPyCodeName({ robotId: _robotId })
}

export function renameProcessName(_robotId: string, _processId: string, _processName: string) {
  return renameProcessApi({ robotId: _robotId, processId: _processId, processName: _processName })
}

export function renameModuleName(_robotId: string, _processId: string, _processName: string) {
  return renameProcessPyCode({ robotId: _robotId, moduleId: _processId, moduleName: _processName })
}

export function deleteProcess(_robotId: string, _processId: string, _processName: string) {
  return delProcess({ processId: _processId, robotId: _robotId, processName: _processName })
}

export function deleteModule(_processId: string) {
  return deleteProcessPyCode(_processId)
}

export function getAtomicSchemaByVersion(atomList: { key: string, version: string }[]): Promise<any[]> {
  return getAbilityInfo(atomList).then((res) => {
    return res.data.map(i => JSON.parse(i))
  })
}

export function getAtomBykey(key: string) {
  return getTreeByParentKey(key).then((res) => {
    return res.data.map(i => JSON.parse(i))
  })
}

export function getSigleNodeAbility(key: string) {
  return getNewAtomDesc(key).then((res) => {
    return [JSON.parse(res.data)]
  })
}
