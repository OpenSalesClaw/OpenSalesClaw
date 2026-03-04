import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { RoleHierarchyItem } from '@/api/roles'
import { Button } from '@/components/ui/button'

interface RoleTreeNodeProps {
  node: RoleHierarchyItem
  children: RoleHierarchyItem[]
  allNodes: RoleHierarchyItem[]
  depth: number
  onDelete: (id: number, name: string) => void
}

function RoleTreeNode({ node, children, allNodes, depth, onDelete }: RoleTreeNodeProps) {
  const navigate = useNavigate()
  const [expanded, setExpanded] = useState(true)
  const hasChildren = children.length > 0

  return (
    <div>
      <div
        className="flex items-center gap-2 py-2 px-3 rounded-md hover:bg-muted/50 group"
        style={{ paddingLeft: `${12 + depth * 20}px` }}
      >
        {/* Expand/collapse chevron */}
        <button
          type="button"
          className="w-4 h-4 shrink-0 text-muted-foreground hover:text-foreground"
          onClick={() => setExpanded((v) => !v)}
        >
          {hasChildren ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className={`transition-transform ${expanded ? 'rotate-90' : ''}`}
            >
              <polyline points="9 18 15 12 9 6" />
            </svg>
          ) : (
            <span className="block w-4" />
          )}
        </button>

        {/* Role info */}
        <button
          type="button"
          className="flex-1 text-left"
          onClick={() => navigate(`/admin/roles/${node.id}`)}
        >
          <span className="text-sm font-medium hover:underline">{node.name}</span>
          {node.description && (
            <span className="ml-2 text-xs text-muted-foreground truncate max-w-xs">{node.description}</span>
          )}
        </button>

        {/* Actions */}
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs"
            onClick={() => navigate(`/admin/roles/${node.id}`)}
          >
            Edit
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs text-destructive hover:text-destructive"
            onClick={() => onDelete(node.id, node.name)}
          >
            Delete
          </Button>
        </div>
      </div>

      {/* Children */}
      {hasChildren && expanded && (
        <div>
          {children.map((child) => (
            <RoleTreeNode
              key={child.id}
              node={child}
              children={allNodes.filter((n) => n.parent_role_id === child.id)}
              allNodes={allNodes}
              depth={depth + 1}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}

interface RoleTreeProps {
  nodes: RoleHierarchyItem[]
  onDelete: (id: number, name: string) => void
}

export default function RoleTree({ nodes, onDelete }: RoleTreeProps) {
  // Root nodes: no parent or parent is deleted/missing
  const nodeIds = new Set(nodes.map((n) => n.id))
  const roots = nodes.filter((n) => n.parent_role_id === null || !nodeIds.has(n.parent_role_id))

  if (nodes.length === 0) {
    return (
      <div className="py-8 text-center text-sm text-muted-foreground">
        No roles yet.
      </div>
    )
  }

  return (
    <div className="rounded-md border divide-y">
      {roots.map((root) => (
        <RoleTreeNode
          key={root.id}
          node={root}
          children={nodes.filter((n) => n.parent_role_id === root.id)}
          allNodes={nodes}
          depth={0}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}
