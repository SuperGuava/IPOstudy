import type { IpoItem } from "@/lib/api";

const STAGES = ["offering", "prelisting", "listed"] as const;

export function IpoStageStrip({ items }: { items: IpoItem[] }) {
  const counts = STAGES.map((stage) => ({
    stage,
    count: items.filter((item) => item.stage.toLowerCase().includes(stage === "prelisting" ? "pre" : stage)).length,
  }));
  const total = counts.reduce((sum, row) => sum + row.count, 0) || 1;

  return (
    <section className="rounded-xl border border-ag-line bg-ag-card/90 p-3">
      <div className="mb-2 text-xs uppercase tracking-wide text-ag-mute">Stage Distribution</div>
      <div className="flex gap-2">
        {counts.map((row) => {
          const width = Math.max(10, Math.round((row.count / total) * 100));
          return (
            <div key={row.stage} className="flex-1">
              <div className="mb-1 flex items-center justify-between text-[11px] text-ag-mute">
                <span className="uppercase">{row.stage}</span>
                <span>{row.count}</span>
              </div>
              <div className="h-2 overflow-hidden rounded bg-ag-panel">
                <div className="h-2 rounded bg-ag-accent" style={{ width: `${width}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
