import { isEmpty, omit } from 'lodash-es'

import { translate } from '@/plugins/i18next'

export interface AtomTreeNode extends Omit<RPA.AtomTreeNode, 'atomics'> {
  uniqueId: string
  atomics?: AtomTreeNode[]
}

/**
 *  addUniqueIdsToTree 函数：递归地为树中的每个节点添加唯一的 ID.
 *
 *  @param {RPA.AtomTreeNode} node  当前正在处理的树节点（或子树的根节点）.
 *  @param {string} path  当前节点到根节点的路径（用于生成 ID）.
 *  @returns {AtomTreeNode}  返回已修改的节点 (添加了 ID).  注意：返回的是一个新的节点对象，而不是直接修改传入的 node.
 */
export function addUniqueIdsToTree(node: RPA.AtomTreeNode, path: string = ''): AtomTreeNode {
  //  基于当前节点的 key 和父节点的 path 构建新的路径.
  const newPath = path ? `${path}/${node.key}` : node.key

  //  创建当前节点的一个浅拷贝，并将新路径设置为其 ID.
  const newNode: AtomTreeNode = {
    ...omit(node, 'atomics'),
    uniqueId: newPath,
  }

  //  如果当前节点有子节点，则递归地为每个子节点添加 ID.
  if (node.atomics) {
    newNode.atomics = node.atomics.map(child => addUniqueIdsToTree(child, newPath))
  }

  //  返回修改后的节点 (浅拷贝), 也就是添加了 id 属性的节点.
  return newNode
}

/**
 * 在树形结构中搜索标题包含关键词的节点，并返回一个新的树形结构，仅包含匹配的节点和它们的祖先。
 * @param treeNodes 原始树的根节点数组
 * @param keyword 要搜索的关键词
 * @returns 一个新的树形结构，只包含匹配关键词的节点和它们的祖先
 */
export function searchTreeAndKeepStructure(treeNodes: AtomTreeNode[], keyword: string): [AtomTreeNode[], string[]] {
  const expandKeys: string[] = []

  function traverse(nodes: AtomTreeNode[] | undefined): AtomTreeNode[] | undefined {
    if (!nodes) {
      return undefined
    }

    const filteredNodes: Array<AtomTreeNode> = []

    for (const node of nodes) {
      let matchedChildren: AtomTreeNode[] | undefined
      if (node.atomics) {
        matchedChildren = traverse(node.atomics)
      }

      const isMatch = translate(node.title).toLowerCase().includes(keyword.toLowerCase())

      if (matchedChildren?.length > 0) {
        expandKeys.push(node.uniqueId)
      }

      if (isMatch || matchedChildren?.length > 0) {
        filteredNodes.push({
          ...node,
          atomics: isEmpty(matchedChildren) ? node.atomics : matchedChildren,
        })
      }
    }

    return filteredNodes.length > 0 ? filteredNodes : undefined
  }

  return [traverse(treeNodes) || [], expandKeys]
}
