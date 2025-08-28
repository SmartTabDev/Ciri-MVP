'use client';

import { Card } from '@/components/ui/card';

const nodeTypes = [
  {
    type: 'Condition',
    label: 'Condition',
    description: 'Add conditional logic',
  },
  {
    type: 'Instruction',
    label: 'Instruction',
    description: 'Add an instruction step',
  },
  {
    type: 'Begin',
    label: 'Begin Conversation',
    description: 'Start a new conversation flow',
  },
  {
    type: 'End',
    label: 'End',
    description: 'End the conversation flow',
  },
];

export function Sidebar() {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <Card className="w-64 p-4 bg-background">
      <h3 className="text-lg font-semibold mb-4">Nodes</h3>
      <div className="space-y-2">
        {nodeTypes.map((node) => (
          <div
            key={node.type}
            className="p-3 border rounded-lg cursor-move hover:bg-accent"
            draggable
            onDragStart={(e) => onDragStart(e, node.type)}
          >
            <div className="font-medium">{node.label}</div>
            <div className="text-sm text-muted-foreground">
              {node.description}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
