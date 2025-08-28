import { toast } from "sonner";
import Icon from "@/components/icon-component";
import { cn } from "@/lib/utils";
import { useMotherStore } from "@/stores/motherStore";
import { useFlowValidator } from "@/modules/flow-builder/hooks/use-flow-validator";
import { useFlowStore } from "@/stores/flowStore";
import { useUser } from "@/contexts/user-context";

export function NavigationBarModule() {
  const [isMobileView] = useMotherStore((s) => [s.view.mobile]);
  const { companyId: storeCompanyId, isSaving, updateFlowBuilderData } = useFlowStore();
  const { user, loading: userLoading } = useUser();
  const companyId = user?.company_id;

  const [isValidating, validateFlow] = useFlowValidator(async (isValid) => {
    if (isValid) {
      try {
        const currentCompanyId = companyId || storeCompanyId;
        if (!currentCompanyId) {
          throw new Error("No company ID available");
        }
        await updateFlowBuilderData(currentCompanyId);
        toast.success("Ciri flow er nå godkjent", {
          description: "Flow data has been saved and AI analysis completed",
        });
      } catch (error: any) {
        console.error('Error updating flow builder data:', error);
        toast.error("Feil ved lagring av flow", {
          description: error.message || "An error occurred while saving the flow",
        });
      }
    } else {
      toast.error("Ciri flow er ikke godkjent", {
        description: "Please fix the validation errors before saving",
      });
    }
  });

  const handleSaveFlow = async () => {
    const currentCompanyId = companyId || storeCompanyId;
    if (!currentCompanyId) {
      toast.error("Ingen bedrift valgt", {
        description: "Please select a company before saving",
      });
      return;
    }
    await validateFlow();
  };

  const isLoading = isValidating || isSaving || userLoading;

  return (
    <div className="flex h-12 items-center justify-between border-b border-[var(--border)] bg-[var(--background)] px-4">
      <div className="flex items-center gap-x-2">
        <div className="flex items-center gap-x-1">
          <Icon name="mynaui:network" className="size-4" />
          <span className="text-sm font-medium">Ciri Flow Builder</span>
        </div>
      </div>

      <div className="flex items-center gap-x-2">
        <button
          type="button"
          className={cn(
            "flex items-center gap-x-1.5 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-xs font-medium transition outline-none hover:bg-[var(--muted)] active:border-[var(--border)] active:bg-[var(--muted)]/50",
            isLoading && "op-50 pointer-events-none cursor-not-allowed",
          )}
          onClick={handleSaveFlow}
          disabled={isLoading}
        >
          {isLoading ? (
            <Icon name="svg-spinners:180-ring" className="size-5" />
          ) : (
            <Icon name="mynaui:check-circle" className="size-5" />
          )}
          <span className="pr-0.5">
            {isLoading ? "Lagrer flow" : "Lagre flow"}
          </span>
        </button>
      </div>
    </div>
  );
}
