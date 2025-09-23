import type { Task } from '@/types/schedule'

import http from './http'
import { getRootBaseURL } from './http/env'

/**
 * @description: 获取计划任务列表数据
 */
export async function getScheduleLst(data) {
  const res = await http.post('/robot/triggerTask/page/list', data)
  return res
}

/**
 * @description: cron表达式校验
 */
export function checkCronExpression(data) {
  return http.post('/robot/task/corn/check', data, { toast: false })
}

/**
 * @description: 获取计划任务执行记录列表数据
 */
export function getTaskExecuteLst(data) {
  return http.post('/robot/task-execute/list', data)
}

/**
 * @description: 倒计时的计划任务取消
 */
export function taskCancel(data) {
  return http.post('/scheduler/crontab/cancel', data, { baseURL: getRootBaseURL() })
}

// 手动触发
export function manualTrigger(data: { task_id: string }) {
  return http.post('/trigger/task/run', data, { baseURL: getRootBaseURL() })
}

// taskNotify 通知触发器更新
export function taskNotify(params = { event: 'normal' }) {
  return http.post('/trigger/task/notify', params, { toast: false, baseURL: getRootBaseURL() })
}

// 获取计划任务未来执行时间
export function taskFutureTime(data: { task_id: string, times: number }) {
  return http.post('/trigger/task/future', data, { baseURL: getRootBaseURL() })
}

// /task/future_with_no_create
export function taskFutureTimeNoCreate(data: { frequency_flag: string, times: number }) {
  return http.post('/trigger/task/future_with_no_create', data, { toast: false, baseURL: getRootBaseURL() })
}

// 重命名校验
export function isNameCopy(data: { name: string }) {
  return http.get('/robot/triggerTask/isNameCopy', data)
}

// 机器人列表
export function getRobotList(data: { name: string }) {
  return http.get('/robot/triggerTask/robotExe/list', data)
}

// 新增计划任务
export async function insertTask(data: Task) {
  const res = await http.post('/robot/triggerTask/insert', data)
  taskNotify()
  return res
}

// 获取单个计划任务接口
export function getTaskInfo(data: { taskId: string }) {
  return http.get('/robot/triggerTask/get', data)
}

// 删除单个计划任务接口
export async function deleteTask(data: { taskId: string }) {
  const res = await http.get('/robot/triggerTask/delete', data)
  taskNotify()
  return res
}
// 更新计划任务接口
export async function updateTask(data: Task) {
  const res = await http.post('/robot/triggerTask/update', data)
  taskNotify()
  return res
}
// 启用/禁用 计划任务
export async function enableTask(data: { taskId: string, enable: number }) {
  const res = await http.get('/robot/triggerTask/enable', data)
  taskNotify()
  return res
}

// 获取计划任务队列状态
export function getTaskQueueList(data) {
  return http.get('/trigger/task/queue/status', data, { baseURL: getRootBaseURL() })
}

// 移除计划任务队列
export function removeTaskQueue(data: { unique_id: string[] }) {
  return http.post('/trigger/task/queue/remove', data, { baseURL: getRootBaseURL() })
}

// 更新计划任务队列配置
export function updateTaskQueueConfig(data: { max_length: number, max_wait_minutes: number, deduplicate: boolean }) {
  return http.post('/trigger/task/queue/config', data, { baseURL: getRootBaseURL() })
}

// 获取计划任务队列配置
export function getTaskQueueConfig() {
  return http.get('/trigger/task/queue/config', {}, { baseURL: getRootBaseURL() })
}
