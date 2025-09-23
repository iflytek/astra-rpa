import { Bus as Event } from '@/utils/eventBus'

import type { ProcessNodeEvent } from '../IProjectDocument'
import type { ProcessNode } from '../type'

import { UndoManager } from './UndoManager'
import type { Operation } from './UndoManager'

/**
 * 实际的流程编辑器逻辑实现。
 * TODO: 对于 move 等操作的索引边界条件、undo/restore 需要测试验证
 */
export class ProcessEditor {
  private id: string
  private nodes: ProcessNode[] | RPA.Atom[]
  private undoManager: UndoManager<ProcessNode>
  emitter = new Event<ProcessNodeEvent>()
  constructor(id: string, nodes: ProcessNode[]) {
    this.id = id
    this.nodes = nodes
    this.undoManager = new UndoManager<ProcessNode>(
      this.applyOperation.bind(this),
    )
  }

  public getNodes() {
    return this.nodes
  }

  public addNode(node: ProcessNode[], index: number[], option: Record<string, unknown>) {
    console.log(option)
    this.undoManager.perform({
      type: 'insert',
      index,
      item: node,
    })
  }

  public deleteNode(nodeIds: string[]) {
    const idxArr = []
    const deleteNodes = nodeIds.map((id) => {
      const idx = this.nodes.findIndex(n => n.id === id)
      idxArr.push(idx)
      return this.nodes[idx]
    })
    this.undoManager.perform({
      type: 'delete',
      index: idxArr,
      item: deleteNodes,
    })
  }

  public updateNode(node: ProcessNode[], index: number[]) {
    const oldNode = index.map(i => this.nodes[i])
    if (!oldNode)
      return
    this.undoManager.perform({
      type: 'update',
      index,
      oldItem: oldNode,
      newItem: node,
    })
  }

  public moveNode(from: number, to: number, conditionId?: string[]) {
    const moveEle = []
    if (conditionId.length > 0) {
      conditionId.forEach((id) => {
        const idx = this.nodes.findIndex(i => i.id === id)
        moveEle.push(this.nodes[idx])
      })
    }
    this.undoManager.perform({
      type: 'move',
      fromIndex: from,
      toIndex: to,
      toPreId: this.nodes[to - from < 0 ? to - 1 : to]?.id,
      fromPreId: this.nodes[from - 1]?.id,
      item: moveEle,
    })
  }

  public canUndo() {
    return this.undoManager.canUndo()
  }

  public undo() {
    return this.undoManager.undo()
  }

  public canRestore() {
    return this.undoManager.canRestore()
  }

  public restore() {
    return this.undoManager.restore()
  }

  public clear() {
    this.nodes.length = 0
    this.undoManager.clear()
  }

  private pushNode(newNodes: ProcessNode[], orderList: number[]) {
    if (orderList.length < newNodes.length) {
      this.nodes.splice(orderList[0], 0, ...newNodes)
      this.emitter.$emit('add', orderList, newNodes, { processId: this.id })
    }
    else {
      const nodeMap = {}
      orderList.forEach((idx, i) => nodeMap[idx] = newNodes[i])
      Object.keys(nodeMap).forEach((idx) => {
        const node = nodeMap[idx]
        this.nodes.splice(Number(idx), 0, node)
      })
      this.emitter.$emit('add', Object.keys(nodeMap).map(i => Number(i)), Object.values(nodeMap), { processId: this.id })
    }
  }

  private deleteLastNode(newNodes: ProcessNode[], orderList: number[]) {
    const ids = newNodes.map(i => i.id)
    this.nodes = this.nodes.filter(node => !ids.includes(node.id))
    this.emitter.$emit('delete', orderList, newNodes, { processId: this.id })
  }

  private applyOperation(operation: Operation<ProcessNode>, isUndo: boolean) {
    let insertId = null
    let elementsToMove = []
    let insertIdx = null
    switch (operation.type) {
      case 'insert':
        if (isUndo) {
          this.deleteLastNode(operation.item, operation.index)
        }
        else {
          this.pushNode(operation.item, operation.index)
        }
        break
      case 'delete':
        if (isUndo) {
          this.pushNode(operation.item, operation.index)
        }
        else {
          this.deleteLastNode(operation.item, operation.index)
        }
        break
      case 'update':
        if (isUndo) {
          operation.index.forEach((i, idx) => {
            this.nodes[i] = operation.oldItem[idx]
          })
        }
        else {
          operation.index.forEach((i, idx) => {
            this.nodes[i] = operation.newItem[idx]
          })
        }
        this.emitter.$emit('update', operation.index, isUndo ? operation.oldItem : operation.newItem, { processId: this.id })
        break
      case 'move':
        insertId = operation.toIndex === 0 ? '' : this.nodes[this.nodes.findIndex(node => node.id === operation.toPreId)].id
        if (isUndo) {
          insertId = operation.fromPreId || ''
        }
        if (operation.item.length > 1) {
          const start = this.nodes.indexOf(operation.item[0])
          const end = this.nodes.indexOf(operation.item[operation.item.length - 1])
          elementsToMove = this.nodes.splice(start, end - start + 1)
        }
        else {
          elementsToMove = this.nodes.splice(isUndo ? operation.toIndex : operation.fromIndex, 1)
        }
        insertIdx = operation.toIndex === 0 ? 0 : this.nodes.findIndex(node => node.id === insertId) + 1
        if (isUndo) {
          insertIdx = operation.fromIndex === 0 ? 0 : this.nodes.findIndex(node => node.id === insertId) + 1
        }
        if (isUndo) {
          this.emitter.$emit('delete', [operation.toIndex], operation.item, { processId: this.id })
          this.nodes.splice(insertIdx, 0, ...operation.item)
          this.emitter.$emit('add', [operation.fromIndex], operation.item, { processId: this.id })
        }
        else {
          this.emitter.$emit('delete', [operation.fromIndex], operation.item, { processId: this.id })
          this.nodes.splice(insertIdx, 0, ...elementsToMove)
          this.emitter.$emit('add', [operation.toIndex], operation.item, { processId: this.id })
        }
        break
    }
    console.log('静态表', this.nodes)
  }
}
