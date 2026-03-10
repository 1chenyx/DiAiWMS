export interface TreeNode {
  id: number
  children?: TreeNode[]
  [key: string]: any
}

export function findTreeNode(nodes: TreeNode[], id: number, path: any[] = []): TreeNode | null {
  for (const node of nodes) {
    if (node.id === id) {
      return { ...node, path }
    }
    if (node.children && node.children.length > 0) {
      const result = findTreeNode(node.children, id, [...path, node])
      if (result) return result
    }
  }
  return null
}

export function getTreeNodePath(nodes: TreeNode[], id: number): TreeNode[] {
  const result = findTreeNode(nodes, id)
  return result?.path || []
}

export function flattenTree(nodes: TreeNode[]): TreeNode[] {
  const result: TreeNode[] = []
  
  function traverse(node: TreeNode) {
    result.push(node)
    if (node.children && node.children.length > 0) {
      node.children.forEach(traverse)
    }
  }
  
  nodes.forEach(traverse)
  return result
}

export function buildTree(
  items: any[],
  options: {
    idKey?: string
    parentIdKey?: string
    childrenKey?: string
  } = {}
): TreeNode[] {
  const {
    idKey = 'id',
    parentIdKey = 'parent_id',
    childrenKey = 'children'
  } = options
  
  const nodeMap = new Map<number, TreeNode>()
  const roots: TreeNode[] = []
  
  items.forEach(item => {
    nodeMap.set(item[idKey], { ...item, [childrenKey]: [] })
  })
  
  items.forEach(item => {
    const node = nodeMap.get(item[idKey])!
    const parentId = item[parentIdKey]
    
    if (parentId && nodeMap.has(parentId)) {
      const parent = nodeMap.get(parentId)!
      if (!parent[childrenKey]) {
        parent[childrenKey] = []
      }
      parent[childrenKey].push(node)
    } else {
      roots.push(node)
    }
  })
  
  return roots
}

export function filterTree(
  nodes: TreeNode[],
  predicate: (node: TreeNode) => boolean
): TreeNode[] {
  return nodes
    .filter(predicate)
    .map(node => {
      if (node.children && node.children.length > 0) {
        const filteredChildren = filterTree(node.children, predicate)
        return { ...node, children: filteredChildren }
      }
      return node
    })
}
