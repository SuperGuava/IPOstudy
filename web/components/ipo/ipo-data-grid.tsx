import type { IpoItem } from "@/lib/api";
import { cn } from "@/lib/utils";

export function IpoDataGrid({
  items,
  selectedId,
  onSelect,
}: {
  items: IpoItem[];
  selectedId?: string;
  onSelect: (item: IpoItem) => void;
}) {
  return (
    <div className="overflow-x-auto rounded-xl border border-ag-line bg-ag-card/90">
      <table className="min-w-full text-left text-[13px]">
        <thead className="border-b border-ag-line bg-ag-panel/80 text-[11px] uppercase tracking-wide text-ag-mute">
          <tr>
            <th className="px-3 py-2">corp_name</th>
            <th className="px-3 py-2">stage</th>
            <th className="px-3 py-2">listing_date</th>
            <th className="px-3 py-2">lead_manager</th>
            <th className="px-3 py-2">status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const isActive = item.pipeline_id === selectedId;
            return (
              <tr
                key={item.pipeline_id}
                className={cn(
                  "cursor-pointer border-b border-ag-line/80 transition hover:bg-ag-panel/70",
                  isActive && "bg-ag-accent/10",
                )}
                onClick={() => onSelect(item)}
              >
                <td className="px-3 py-2 font-medium">{item.corp_name}</td>
                <td className="px-3 py-2 text-ag-mute">{item.stage}</td>
                <td className="px-3 py-2 text-ag-mute">{item.listing_date ?? "-"}</td>
                <td className="px-3 py-2 text-ag-mute">{item.lead_manager ?? "-"}</td>
                <td className="px-3 py-2">
                  <span className="rounded border border-ag-accent/40 bg-ag-accent/10 px-2 py-0.5 text-[11px] text-ag-accent">
                    tracked
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
