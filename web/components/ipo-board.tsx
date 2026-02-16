"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { IpoDataGrid } from "@/components/ipo/ipo-data-grid";
import { IpoDetailDrawer } from "@/components/ipo/ipo-detail-drawer";
import { IpoKpiStrip } from "@/components/ipo/ipo-kpi-strip";
import { IpoStageStrip } from "@/components/ipo/ipo-stage-strip";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { IpoItem, RefreshMeta } from "@/lib/api";

export function IpoBoard({
  items,
  refresh,
  corpCode,
  basDd,
}: {
  items: IpoItem[];
  refresh?: RefreshMeta;
  corpCode: string;
  basDd: string;
}) {
  const [selected, setSelected] = useState<IpoItem | undefined>(items[0]);

  const sourceEntries = useMemo(
    () => Object.entries(refresh?.source_status ?? {}).sort(([a], [b]) => a.localeCompare(b)),
    [refresh],
  );

  return (
    <section className="space-y-4">
      <div className="rounded-xl border border-ag-line bg-ag-panel/80 p-3">
        <form className="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
          <input type="hidden" name="refresh" value="true" />
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-ag-mute">corp_code</span>
            <input
              name="corp_code"
              defaultValue={corpCode}
              className="w-full rounded-md border border-ag-line bg-ag-card px-2 py-1.5 text-sm outline-none focus:border-ag-accent"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-ag-mute">bas_dd (YYYYMMDD)</span>
            <input
              name="bas_dd"
              defaultValue={basDd}
              className="w-full rounded-md border border-ag-line bg-ag-card px-2 py-1.5 text-sm outline-none focus:border-ag-accent"
            />
          </label>
          <div className="flex items-end gap-2">
            <button
              type="submit"
              className="rounded-md border border-ag-accent/50 bg-ag-accent/10 px-3 py-1.5 text-xs font-semibold text-ag-accent hover:bg-ag-accent/20"
            >
              Refresh Pipeline
            </button>
          </div>
        </form>
      </div>

      <IpoKpiStrip items={items} refresh={refresh} />
      <IpoStageStrip items={items} />

      <div className="grid gap-4 xl:grid-cols-[1fr_320px]">
        <div className="space-y-3">
          <IpoDataGrid items={items} selectedId={selected?.pipeline_id} onSelect={setSelected} />
          <Card>
            <div className="text-[11px] uppercase tracking-wide text-ag-mute">Quick Navigate</div>
            <div className="mt-2 flex flex-wrap gap-2">
              {items.slice(0, 6).map((item) => (
                <Link
                  key={item.pipeline_id}
                  href={`/ipo/${item.pipeline_id}`}
                  className="rounded border border-ag-line px-2 py-1 text-xs text-ag-mute hover:border-ag-accent/50 hover:text-ag-text"
                >
                  {item.corp_name}
                </Link>
              ))}
            </div>
          </Card>
        </div>
        <div className="space-y-3">
          <IpoDetailDrawer item={selected} refresh={refresh} />
          <Card>
            <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Source Meta</div>
            <div className="flex flex-wrap gap-2">
              {sourceEntries.length > 0 ? (
                sourceEntries.map(([key, value]) => {
                  const tone = value.includes("ok") ? "ok" : value.includes("auth") ? "fail" : "warn";
                  return <Badge key={key} label={`${key}:${value}`} tone={tone} />;
                })
              ) : (
                <Badge label="no_refresh_meta" tone="muted" />
              )}
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}
