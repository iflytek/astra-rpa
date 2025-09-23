import type { NodeID, ProcessNode } from '@/ast/ASTNode'
import { ASTNode } from '@/ast/ASTNode'
import { CATCH_TEXT, ELSE_IF_TEXT, ELSE_TEXT, FINALLY_TEXT, FOR_BRO_SIMILAR, FOR_DICT_TEXT, FOR_END_TEXT, FOR_EXCEL_CONTENT, FOR_LIST_TEXT, FOR_STEP_TEXT, GROUP_END_TEXT, GROUP_TEXT, IF_END_TEXT, IF_TEXT, TRY_END_TEXT, TRY_TEXT, WHILE_TEXT } from '@/views/Arrange/config/atomKeyMap'

export class IncrementalASTParser {
  private root: ASTNode
  private nodeMap = new Map<NodeID, ASTNode>()
  private dirtyQueue = new Set<ASTNode>()
  private isBatching = false
  private pendingBatch: number | null = null

  constructor(initialNodes: ProcessNode[]) {
    this.root = this.buildFullTree(initialNodes)
  }

  private buildFullTree(nodes: ProcessNode[]): ASTNode {
    const root = new ASTNode({ id: 'root', type: 'root' })
    const stack: ASTNode[] = [root]

    nodes.forEach((rawNode) => {
      const node = new ASTNode(rawNode)
      this.nodeMap.set(rawNode.id, node)
      node.parent = stack[stack.length - 1]
      if (this.isContainerType(rawNode.type)) {
        stack.push(node)
      }
      else if (this.isEndType(rawNode.type)) {
        stack.pop()
      }
      this.finalizeNode(node)
    })
    this.flushChanges()

    return root
  }

  public batchUpdate(callback: () => void) {
    this.isBatching = true
    callback()
    this.isBatching = false
    this.flushUpdates()
  }

  private flushChanges() {
    this.processDirtyQueue()
  }

  private flushUpdates() {
    if (this.pendingBatch) {
      cancelAnimationFrame(this.pendingBatch)
    }
    this.pendingBatch = requestAnimationFrame(() => {
      this.processDirtyQueue()
      this.pendingBatch = null
    })
  }

  public moveNodeAfter(originId: string, afterId: string, insertIdx: number) {
    const originNode = this.nodeMap.get(originId)
    if (!originNode)
      return
    const parent = originNode.parent
    parent.removeChild(originNode)
    this.insertNodeAfter(afterId, insertIdx, [originNode], false, false)
    this.traverseSubtree(originNode, (n) => {
      this.finalizeNode(n)
    })
  }

  public deleteNode(nodeId: string) {
    const node = this.nodeMap.get(nodeId)
    if (!node)
      return
    if (!node.parent)
      throw new Error('不能移除根节点')
    const nodeType = node.raw.type
    const parent = node.parent
    const children = node.children.slice(0, -1)
    const idx = parent.children.indexOf(node)
    if (nodeType === GROUP_TEXT) {
      node.children.length = 0
    }
    parent.removeChild(node)
    if (nodeType === GROUP_TEXT) {
      parent.insertChild(idx, children)
      children.forEach((child) => {
        this.traverseSubtree(child, (n) => {
          this.finalizeNode(n)
        })
      })
    }
    this.traverseSubtree(node, (n) => {
      this.nodeMap.delete(n.id)
      n.parent = null
    })
    this.finalizeNode(parent)
    this.flushChanges()
  }

  public createGroup(groupIds: string[], insertIds: string[]) {
    const insertFirstNode = this.nodeMap.get(insertIds[0])
    const insertLastNode = this.nodeMap.get(insertIds[1])
    if (!insertFirstNode)
      return

    const groupParent = insertFirstNode.parent
    const firstIndex = insertFirstNode.parent.children.indexOf(insertFirstNode)
    let lastIndex = -1
    const startNode = new ASTNode({ id: groupIds[0], type: GROUP_TEXT })
    const endNode = new ASTNode({ id: groupIds[1], type: GROUP_END_TEXT })

    this.safeInsert({
      parent: groupParent,
      index: firstIndex,
      nodes: [startNode, endNode],
    })
    if (this.isContainerType(insertFirstNode.type) && this.isEndType(insertLastNode.type)) {
      startNode.insertChild(0, [insertFirstNode])
    }
    else {
      let insertNode = insertLastNode
      if (this.isEndType(insertLastNode.type)) {
        insertNode = insertLastNode.parent
      }
      lastIndex = groupParent.children.indexOf(insertNode)
      const child = groupParent.children.slice(firstIndex + 1, lastIndex + 1)
      startNode.insertChild(0, child)
    }
    this.traverseSubtree(startNode, (n) => {
      this.finalizeNode(n)
    })
    this.flushChanges()
  }

  public insertNodeAfter(targetId: string, insertIdx: number, newNodeData: ProcessNode[] | ASTNode[], isUINull: boolean, isAdd: boolean = true) {
    let parentNode = this.root
    let targetIndex = 0
    if (isUINull)
      this.nodeMap.clear()
    if (insertIdx !== 0 && this.nodeMap.size !== 0) {
      const targetNode = this.nodeMap.get(targetId)
      if (!targetNode)
        throw new Error(`目标节点 ${targetId} 不存在`)
      parentNode = this.defineParent(targetNode, newNodeData[0].type)
      if (!parentNode)
        throw new Error(`目标节点 ${targetId} 没有父节点`)
      const siblings = parentNode.children
      targetIndex = siblings.indexOf(this.isEndType(targetNode.type) ? targetNode.parent : targetNode)
    }
    const newNodes = isAdd
      ? (newNodeData as ProcessNode[]).map(node => new ASTNode(node))
      : (newNodeData as ASTNode[])
    this.safeInsert({
      parent: parentNode,
      index: insertIdx === 0 ? targetIndex : targetIndex + 1,
      nodes: newNodes,
    })
    this.markRelatedDirty(newNodes)
    if (newNodes.length < 2) {
      this.finalizeNode(newNodes[0])
    }
    else {
      newNodes.forEach(node => this.finalizeNode(node))
    }
    this.flushChanges()
  }

  private safeInsert(params: {
    parent: ASTNode
    index: number
    nodes: ASTNode[]
  }) {
    const { parent, index, nodes } = params
    nodes.some((node) => {
      if (this.checkCyclic(parent, node)) {
        throw new Error('存在循环引用')
      }
      return false
    })
    const stack: ASTNode[] = [parent]
    let idx = index
    nodes.forEach((node) => {
      this.nodeMap.set(node.id, node)
      stack[stack.length - 1].insertChild(idx, [node])
      idx = stack[stack.length - 1].children.indexOf(node) + 1
      if (this.isContainerType(node.type)) {
        stack.push(node)
        idx = 0
      }
      else if (this.isEndType(node.type)) {
        stack.pop()
      }
    })
  }

  private checkCyclic(parent: ASTNode, node: ASTNode): boolean {
    let current: ASTNode | null = parent
    while (current) {
      if (current === node)
        return true
      current = current.parent
    }
    return false
  }

  private markRelatedDirty(nodes: ASTNode[]) {
    nodes.forEach((node) => {
      if (!node.isDirty('structure')) {
        node.markDirty('structure')
      }
      let current: ASTNode | null = node
      while (current) {
        if (!node.isDirty('level')) {
          node.markDirty('level')
        }
        current = current.parent
      }
    })
  }

  private traverseSubtree(root: ASTNode, callback: (node: ASTNode) => void) {
    const stack = [root]
    while (stack.length > 0) {
      const node = stack.pop()
      callback(node)
      stack.push(...node.children)
    }
  }

  private processDirtyQueue() {
    const levelMap = new Map<number, ASTNode[]>()
    this.dirtyQueue.forEach((node) => {
      const level = node.level
      if (!levelMap.has(level)) {
        levelMap.set(level, [])
      }
      levelMap.get(level)!.push(node)
    })
    const sortedLevels = Array.from(levelMap.keys()).sort((a, b) => a - b)
    sortedLevels.forEach((level) => {
      levelMap.get(level)!.forEach((node) => {
        if (node.isDirty('level')) {
          const newLevel = node.calculateLevel()
          if (node.level !== newLevel) {
            node.level = newLevel
            node.markDirty('level', true)
          }
          node.clearDirty('level')
        }
        if (node.isDirty('structure')) {
          this.validateNodeStructure(node)
          node.clearDirty('structure')
        }
        // if (node.isDirty('error')) {
        //     this.validateNodeErrors(node);
        //     node.clearDirty('error');
        // }
      })
    })
    this.dirtyQueue.clear()
  }

  private validateNodeStructure(node: ASTNode) {
    switch (node.type) {
      case IF_TEXT:
        if (!this.hasRelatedChild(node, IF_END_TEXT))
          node.raw.error = `${node.type}缺少${IF_END_TEXT}结束标记`
        break
      case ELSE_IF_TEXT:
      case ELSE_TEXT:
      case IF_END_TEXT:
        this.hasRelatedParent(node, [IF_TEXT])
        break
      case FOR_STEP_TEXT:
      case FOR_DICT_TEXT:
      case FOR_EXCEL_CONTENT:
      case FOR_BRO_SIMILAR:
      case FOR_LIST_TEXT:
      case WHILE_TEXT:
        if (!this.hasRelatedChild(node, FOR_END_TEXT))
          node.raw.error = `${node.type}缺少${FOR_END_TEXT}结束标记`
        break
      case FOR_END_TEXT:
        this.hasRelatedParent(node, [FOR_STEP_TEXT, FOR_DICT_TEXT, FOR_EXCEL_CONTENT, FOR_BRO_SIMILAR, FOR_LIST_TEXT, WHILE_TEXT])
        break
      case GROUP_TEXT:
        if (!this.hasRelatedChild(node, GROUP_END_TEXT))
          node.raw.error = `${node.type}缺少${GROUP_END_TEXT}结束标记`
        break
      case GROUP_END_TEXT:
        this.hasRelatedParent(node, [GROUP_TEXT])
        break
      case TRY_TEXT:
        if (!this.hasRelatedChild(node, TRY_END_TEXT))
          node.raw.error = `${node.type}缺少${TRY_END_TEXT}结束标记`
        break
      case CATCH_TEXT:
      case FINALLY_TEXT:
      case TRY_END_TEXT:
        this.hasRelatedParent(node, [TRY_TEXT])
        break
      default:
        break
    }
  }

  // private validateNodeErrors(node: ASTNode) {
  //     console.log(node);
  // }

  private finalizeNode(node: ASTNode, parentLevel?: number) {
    if (parentLevel) {
      node.level = parentLevel
    }
    else if (this.isEndType(node.raw.type)) {
      node.level = node.parent.level
    }
    else {
      node.level = node.calculateLevel()
    }
    node.clearDirty('level')
    this.dirtyQueue.add(node)
  }

  private defineParent(targetNode: ASTNode, newNodeType: string) {
    const { raw } = targetNode
    if ([ELSE_IF_TEXT, ELSE_TEXT, CATCH_TEXT, FINALLY_TEXT].includes(raw.type)) {
      return [IF_END_TEXT, ELSE_TEXT, ELSE_IF_TEXT, TRY_END_TEXT].includes(newNodeType) ? targetNode.parent : targetNode
    }
    else if ([IF_TEXT, TRY_TEXT, FOR_STEP_TEXT, FOR_DICT_TEXT, FOR_EXCEL_CONTENT, FOR_BRO_SIMILAR, FOR_LIST_TEXT, WHILE_TEXT, GROUP_TEXT].includes(raw.type)) {
      return targetNode
    }
    else if ([IF_END_TEXT, FOR_END_TEXT, GROUP_END_TEXT, TRY_END_TEXT].includes(raw.type)) {
      return targetNode.parent.parent
    }
    else {
      return targetNode.parent
    }
  }

  private isContainerType(type: string): boolean {
    return [IF_TEXT, FOR_STEP_TEXT, FOR_DICT_TEXT, FOR_EXCEL_CONTENT, FOR_BRO_SIMILAR, FOR_LIST_TEXT, WHILE_TEXT, TRY_TEXT, GROUP_TEXT].includes(type)
  }

  private isEndType(type: string): boolean {
    return [IF_END_TEXT, GROUP_END_TEXT, FOR_END_TEXT, TRY_END_TEXT].includes(type)
  }

  private hasRelatedParent(node: ASTNode, types: string[]) {
    const current = node.parent
    const flag = types.includes(current?.type)
    const text = node.type === FOR_END_TEXT ? 'for' : types[0]
    if (flag) {
      current.raw.error = ''
    }
    else {
      node.raw.error = `${node.type}缺少对应的${text}节点`
    }
  }

  private hasRelatedChild(node: ASTNode, type: string): boolean {
    return node.children.some(c => c.type === type)
  }

  getNode(id: NodeID): ASTNode | undefined {
    const node = this.nodeMap.get(id)
    return node
  }

  getAllNodeMap() {
    return this.nodeMap
  }

  clear() {
    this.nodeMap.clear()
    this.dirtyQueue.clear()
    this.root = new ASTNode({ id: 'root', type: 'root' })
  }
}
