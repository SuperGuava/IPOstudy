import { Card } from "@/components/ui/card";
import type { IpoItem, RefreshMeta } from "@/lib/api";

function countStage(items: IpoItem[], matcher: (stage: string) => boolean): number {
  return items.filter((item) => matcher(item.stage.toLowerCase())).length;
}

export function IpoKpiStrip({ items, refresh }: { items: IpoItem[]; refresh?: RefreshMeta }) {
  const total = items.length;
  const offering = countStage(items, (stage) => stage.includes("offer"));
  const preListing = countStage(items, (stage) => stage.includes("pre"));
  const listed = countStage(items, (stage) => stage.includes("list"));
  const refreshLabel = refresh
    ? `${refresh.published ? "Published" : "Blocked"} / issues ${refresh.issue_count}`
    : "No refresh";

  const cards = [
    { label: "Total IPO", value: String(total) },
    { label: "Offering", value: String(offering) },
    { label: "Pre-Listing", value: String(preListing) },
    { label: "Completed", value: String(listed) },
    { label: "Refresh", value: refreshLabel },
  ];

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
      {cards.map((card, idx) => (
        <Card key={card.label} className="animate-fade-up" style={{ animationDelay: `${idx * 40}ms` }}>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">{card.label}</div>
          <div className="mt-1 text-base font-semibold md:text-lg">{card.value}</div>
        </Card>
      ))}
    </div>
  );
}
