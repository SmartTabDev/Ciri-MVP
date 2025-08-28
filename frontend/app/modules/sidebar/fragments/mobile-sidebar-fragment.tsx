"use client";
import { useEffect } from "react";
import { toast } from "sonner";
import { Drawer } from "vaul";

import type { ApplicationState } from "@/stores/application-state";

import { useFlowValidator } from "@/modules/flow-builder/hooks/use-flow-validator";
import { SwitchSidebarPanel } from "@/modules/sidebar/components/sidebar-switch-panel";

import { OnMounted } from "@/components/training/on-mounted";
import { Switch } from "@/components/training/switch-case";
import { cn } from "@/lib/utils";
import Icon from "@/components/icon-component";

type MobileSidebarFragmentProps = Readonly<{
  activePanel: ApplicationState["sidebar"]["active"];
  setActivePanel: (panel: ApplicationState["sidebar"]["active"]) => void;
}>;

export function MobileSidebarFragment({
  activePanel,
  setActivePanel,
}: MobileSidebarFragmentProps) {
  const [isValidating, validateFlow] = useFlowValidator((isValid) => {
    if (isValid) {
      toast.success("Flow is valid", {
        description: "You can now proceed to the next step",
        dismissible: true,
      });
    } else {
      toast.error("Flow is invalid", {
        description:
          "Please check if the flow is complete and has no lone nodes",
      });
    }
  });

  useEffect(() => {
    setActivePanel("none");
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <>
      <div className="pointer-events-none absolute right-0 bottom-0 left-0 flex touch-none items-center justify-center p-4">
        <div className="pointer-events-auto flex touch-auto items-center gap-x-0.5 rounded-full border border-[var(--border)] bg-[var(--background)]/80 p-1 shadow-xl shadow-black/20 backdrop-blur-2xl">
          <button
            onClick={() => setActivePanel("available-nodes")}
            type="button"
            className="flex size-10 shrink-0 items-center justify-center rounded-full border border-transparent bg-transparent transition outline-none active:border-[var(--border)] active:bg-[var(--muted)]"
          >
            <Icon name="mynaui:grid" className="size-5" />
          </button>

          <button
            onClick={() => setActivePanel("node-properties")}
            type="button"
            className="flex size-10 shrink-0 items-center justify-center rounded-full border border-transparent bg-transparent transition outline-none active:border-[var(--border)] active:bg-[var(--muted)]"
          >
            <Icon name="mynaui:layers-three" className="size-5" />
          </button>

          <div className="h-4 w-px shrink-0 bg-[var(--border)]" />

          <button
            onClick={() => validateFlow()}
            type="button"
            data-is-validating={isValidating}
            className="flex size-10 shrink-0 cursor-not-allowed items-center justify-center rounded-full border border-transparent bg-transparent transition outline-none active:border-[var(--border)] active:bg-[var(--muted)] data-[is-validating=true]:pointer-events-none data-[is-validating=true]:opacity-50"
          >
            <Switch match={isValidating}>
              <Switch.Case value>
                <Icon name="svg-spinners:180-ring" className="size-5" />
              </Switch.Case>
              <Switch.Case value={false}>
                <Icon name="mynaui:check-circle" className="size-5" />
              </Switch.Case>
            </Switch>
          </button>

          <div className="h-4 w-px shrink-0 bg-[var(--border)]" />
        </div>
      </div>

      <OnMounted>
        <Drawer.Root
          noBodyStyles
          open={activePanel !== "none"}
          onOpenChange={(open) => {
            if (!open) setActivePanel("none");
          }}
        >
          <Drawer.Portal>
            <Drawer.Overlay className="fixed inset-0 bg-[var(--background)]/60" />
            <Drawer.Content
              className={cn(
                "max-h-90% fixed right-0 bottom-0 left-0 mt-24 flex flex-col overflow-clip rounded-t-3xl bg-[var(--background)] text-[var(--foreground)] shadow-2xl shadow-[0px_-20px_40px_0px_rgba(0,0,0,0.2)] ring-1 ring-[var(--border)] outline-none",
                activePanel === "node-properties" && "h-90%",
              )}
            >
              <SwitchSidebarPanel active={activePanel} />
            </Drawer.Content>
          </Drawer.Portal>
        </Drawer.Root>
      </OnMounted>
    </>
  );
}
