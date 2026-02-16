import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { IpoItem, RefreshMeta } from "@/lib/api";

export function IpoDetailDrawer({
  item,
  refresh,
}: {
  item?: IpoItem;
  refresh?: RefreshMeta;
}) {
  if (!item) {
    return (
      <Card className="h-full">
        <div className="text-xs uppercase tracking-wide text-ag-mute">Detail</div>
        <p className="mt-2 text-sm text-ag-mute">Select a row to inspect source metadata.</p>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <div className="mb-3 flex items-center justify-between">
        <div className="text-xs uppercase tracking-wide text-ag-mute">Detail Drawer</div>
        <Badge label={item.stage} tone="muted" />
      </div>

      <div className="space-y-2 text-sm">
        <div>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Company</div>
          <div className="font-semibold">{item.corp_name}</div>
        </div>
        <div>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Pipeline ID</div>
          <div className="font-mono text-xs">{item.pipeline_id}</div>
        </div>
        <div>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">DART receipt</div>
          <div className="font-mono text-xs">{item.source_dart_rcept_no ?? "-"}</div>
        </div>
      </div>

      <div className="mt-4 space-y-2">
        <div className="text-[11px] uppercase tracking-wide text-ag-mute">Source Status</div>
        <div className="flex flex-wrap gap-2">
          {Object.entries(refresh?.source_status ?? {}).map(([key, value]) => {
            const tone = value.includes("ok") ? "ok" : value.includes("auth") ? "fail" : "warn";
            return <Badge key={key} label={`${key}:${value}`} tone={tone} />;
          })}
        </div>
      </div>

      <div className="mt-4">
        <Link
          href={`/ipo/${item.pipeline_id}`}
          className="inline-flex rounded-md border border-ag-line px-3 py-1.5 text-xs text-ag-text hover:border-ag-accent/50"
        >
          Open Full Detail
        </Link>
      </div>
    </Card>
  );
}
