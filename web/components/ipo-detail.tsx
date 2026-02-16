import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { IpoItem } from "@/lib/api";

export function IpoDetail({ item }: { item: IpoItem }) {
  return (
    <Card className="max-w-3xl">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-xl font-semibold">IPO Detail</h2>
        <Badge label={item.stage} tone="muted" />
      </div>
      <dl className="grid gap-3 text-sm md:grid-cols-2">
        <div>
          <dt className="text-[11px] uppercase tracking-wide text-ag-mute">Company</dt>
          <dd className="font-medium">{item.corp_name}</dd>
        </div>
        <div>
          <dt className="text-[11px] uppercase tracking-wide text-ag-mute">Pipeline ID</dt>
          <dd className="font-mono text-xs">{item.pipeline_id}</dd>
        </div>
        <div>
          <dt className="text-[11px] uppercase tracking-wide text-ag-mute">Listing Date</dt>
          <dd>{item.listing_date ?? "-"}</dd>
        </div>
        <div>
          <dt className="text-[11px] uppercase tracking-wide text-ag-mute">Lead Manager</dt>
          <dd>{item.lead_manager ?? "-"}</dd>
        </div>
      </dl>

      <div className="mt-4">
        <Link
          href={`/company/${item.corp_code ?? "00126380"}`}
          className="inline-flex rounded-md border border-ag-line px-3 py-1.5 text-xs text-ag-text hover:border-ag-accent/50"
        >
          Open Company Snapshot
        </Link>
      </div>
    </Card>
  );
}
