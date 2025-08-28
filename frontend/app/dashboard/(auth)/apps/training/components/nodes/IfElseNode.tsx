'use client';

import { Handle, Position, Node } from 'reactflow';
import { Card } from '@/components/ui/card';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useState } from 'react';

export function IfElseNode({
  data,
  id,
}: {
  data: { label: string };
  id: string;
}) {
  const [label, setLabel] = useState(data.label);
  const [isEditing, setIsEditing] = useState(false);

  const onDelete = () => {
    // @ts-ignore - ReactFlow types are not complete
    const reactFlowInstance = window.reactFlowInstance;
    if (reactFlowInstance) {
      reactFlowInstance.deleteElements({ nodes: [{ id }] });
    }
  };

  const handleLabelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLabel(e.target.value);
  };

  const handleLabelBlur = () => {
    setIsEditing(false);
    // @ts-ignore - ReactFlow types are not complete
    const reactFlowInstance = window.reactFlowInstance;
    if (reactFlowInstance) {
      reactFlowInstance.setNodes((nodes: Node[]) =>
        nodes.map((node: Node) => {
          if (node.id === id) {
            return { ...node, data: { ...node.data, label } };
          }
          return node;
        }),
      );
    }
  };

  return (
    <Card className="p-4 group relative w-[200px] border-2 border-blue-500 shadow-lg gap-0">
      <Handle
        type="target"
        position={Position.Top}
        className="!w-3 !h-3 !-top-2 !bg-white !border-2 !border-gray-500 !rounded-full"
      />
      <div className="font-medium min-h-[24px] text-center">
        {isEditing ? (
          <Input
            value={label}
            onChange={handleLabelChange}
            onBlur={handleLabelBlur}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleLabelBlur();
              }
            }}
            className="h-6 text-sm text-center"
            autoFocus
          />
        ) : (
          <div onClick={() => setIsEditing(true)} className="cursor-text">
            {label}
          </div>
        )}
      </div>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity absolute -top-2 -right-2"
        onClick={onDelete}
      >
        <X className="h-4 w-4" />
      </Button>
      <div>
        <Handle
          type="source"
          position={Position.Bottom}
          id="true"
          className="!w-3 !h-3 !-bottom-2 !bg-white !border-2 !border-gray-500 !rounded-full"
        />
        <div className="absolute bottom-[2px] left-1/2 transform -translate-x-1/2 text-xs text-muted-foreground">
          Yes
        </div>
      </div>
      <div>
        <Handle
          type="source"
          position={Position.Right}
          id="false"
          className="!w-3 !h-3 !-right-2 !bg-white !border-2 !border-gray-500 !rounded-full"
        />
        <div className="absolute top-1/2 right-[8px] transform -translate-y-1/2 text-xs text-muted-foreground">
          No
        </div>
      </div>
    </Card>
  );
}
