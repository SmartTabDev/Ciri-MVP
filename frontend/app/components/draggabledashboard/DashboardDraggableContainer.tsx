"use client";
import { SortableContext, useSortable, arrayMove } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  KeyboardSensor,
  useSensors,
  useSensor,
} from "@dnd-kit/core";
import { GripVertical as DotsSixVertical } from "lucide-react";
import React, { Fragment, useState } from "react";
import {
  LeadBySourceCard,
  SubscriptionsCard,
  TableOrderStatus,
  SummaryCards,
} from "@/components";
import BigCalendar from "../event-calendar/big-calendar";

export const DragHandle: React.FC = () => (
  <button
    className="flex h-[30px] w-[30px] cursor-grab items-center justify-center transition-all active:cursor-grabbing"
    aria-label="Drag handle"
  >
    <DotsSixVertical size={20} />
  </button>
);

const DraggableCard = ({
  id,
  children,
}: {
  id: string;
  children: React.ReactNode;
}) => {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition: transition || "transform 0.2s ease",
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} role="div">
      <Fragment>{children}</Fragment>
      <div {...listeners} id={`handle-${id}`} className="top-4 right-3">
        <DragHandle />
      </div>
    </div>
  );
};

function DashboardDraggableContainer() {
  const [items, setItems] = useState([
    {
      id: "1",
      content: <SummaryCards />,
    },
    {
      id: "2",
      content: <TableOrderStatus />,
    },
    {
      id: "3",
      content: <SubscriptionsCard />,
    },
    {
      id: "4",
      content: <LeadBySourceCard />,
    },
    {
      id: "5",
      content: <BigCalendar />,
    },
  ]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor),
  );

  const handleDragEnd = (e: any) => {
    const { active, over } = e;

    if (active.id !== over.id) {
      setItems((prevItems) => {
        const oldIndex = prevItems.findIndex((item) => item.id === active.id);
        const newIndex = prevItems.findIndex((item) => item.id === over.id);
        return arrayMove(prevItems, oldIndex, newIndex);
      });
    }
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <SortableContext items={items.map((item) => item.id)}>
        <div className="relative w-full">
          {items.map((item) => (
            <Fragment key={item.id}>
              <DraggableCard id={item.id}>{item.content}</DraggableCard>
            </Fragment>
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}

export default DashboardDraggableContainer;
