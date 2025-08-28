import {
  BezierEdge,
  EdgeLabelRenderer,
  type EdgeProps,
  getBezierPath,
  useReactFlow,
} from "@xyflow/react";
import Icon from "@/components/icon-component";

export default function CustomDeletableEdge(props: EdgeProps) {
  const {
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
  } = props;

  const { setEdges } = useReactFlow();

  const [_, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      <BezierEdge {...props} />
      <EdgeLabelRenderer>
        <button
          type="button"
          className="group pointer-events-auto absolute flex size-5 items-center justify-center rounded-full ring-1 transition-colors bg-[var(--destructive)] text-[var(--destructive-foreground)] hover:bg-[var(--muted)] hover:text-[var(--destructive)] hover:ring-[var(--destructive)]"
          style={{
            transform: `translate(${labelX}px, ${labelY}px) translate(-50%, -50%)`,
          }}
          onClick={() =>
            setEdges((edges) => edges.filter((edge) => edge.id !== id))
          }
        >
          <Icon name="maki:cross" className="group-hover:(scale-80) size-3 transition" />
        </button>
      </EdgeLabelRenderer>
    </>
  );
}
