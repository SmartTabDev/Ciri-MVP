'use client';

import { Handle, Position } from 'reactflow';
import { Card } from '@/components/ui/card';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function BeginConversationNode({
  data,
  id,
}: {
  data: { label: string };
  id: string;
}) {
  const onDelete = () => {
    // @ts-ignore - ReactFlow types are not complete
    const reactFlowInstance = window.reactFlowInstance;
    if (reactFlowInstance) {
      reactFlowInstance.deleteElements({ nodes: [{ id }] });
    }
  };

  return (
    <Card className="p-4 group relative w-[200px] border-2 border-green-500 shadow-lg bg-green-50">
      <div className="font-medium min-h-[24px] text-center">{data.label}</div>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity absolute -top-2 -right-2"
        onClick={onDelete}
      >
        <X className="h-4 w-4" />
      </Button>
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-3 !h-3 !-bottom-2 !bg-white !border-2 !border-gray-500 !rounded-full"
      />
    </Card>
  );
}
