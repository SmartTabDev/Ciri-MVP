import Icon from "@/components/icon-component";

export default function IntroductionPropertyPanel() {
    return (
        <div className="h-full flex flex-col items-center justify-center p-4 text-center">
            <div className="size-12 flex items-center justify-center rounded-full bg-[var(--primary)]">
                <Icon name="mynaui:cog-one" className="size-6 text-[var(--primary-foreground)]" />
            </div>

            <div className="mt-4 text-balance text-[var(--primary)] font-medium">
                Node Properties
            </div>

            <div className="mt-1 w-2.5/3 text-xs text-[var(--muted-foreground)]/40 font-medium leading-normal">
                Here you can view and edit the properties of the selected node.
            </div>

            <div className="mt-8 w-full text-xs text-[var(--muted-foreground)]/40 font-medium italic">
                Select a node from the list on the top to view its properties.
            </div>
        </div>
    );
}
