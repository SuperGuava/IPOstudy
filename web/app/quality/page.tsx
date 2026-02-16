import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { getQualityIssues, getQualitySummary } from "@/lib/api";

function textParam(value: string | string[] | undefined): string {
  return typeof value === "string" ? value : "";
}

export default async function QualityPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const source = textParam(params.source);
  const severity = textParam(params.severity);
  const fromDate = textParam(params.from);
  const toDate = textParam(params.to);

  const [issueData, summaryData] = await Promise.all([
    getQualityIssues({
      source: source || undefined,
      severity: severity || undefined,
      fromDate: fromDate || undefined,
      toDate: toDate || undefined,
    }).catch(() => ({ items: [], total: 0 })),
    getQualitySummary({
      source: source || undefined,
      fromDate: fromDate || undefined,
      toDate: toDate || undefined,
    }).catch(() => ({ items: [], total: 0 })),
  ]);

  const latest = summaryData.items[0];

  return (
    <AppShell title="Quality" subtitle="Source issue and summary analytics surface">
      <Card className="mb-4">
        <form className="grid gap-3 md:grid-cols-[1fr_1fr_1fr_1fr_auto]">
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-ag-mute">source</span>
            <input
              name="source"
              defaultValue={source}
              placeholder="DART / KIND / KRX / CROSS"
              className="w-full rounded-md border border-ag-line bg-ag-card px-2 py-1.5 text-sm outline-none focus:border-ag-accent"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-ag-mute">severity</span>
            <select
              name="severity"
              defaultValue={severity}
              className="w-full rounded-md border border-ag-line bg-ag-card px-2 py-1.5 text-sm outline-none focus:border-ag-accent"
            >
              <option value="">all</option>
              <option value="PASS">PASS</option>
              <option value="WARN">WARN</option>
              <option value="FAIL">FAIL</option>
            </select>
          </label>
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-ag-mute">from</span>
            <input
              type="date"
              name="from"
              defaultValue={fromDate}
              className="w-full rounded-md border border-ag-line bg-ag-card px-2 py-1.5 text-sm outline-none focus:border-ag-accent"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-ag-mute">to</span>
            <input
              type="date"
              name="to"
              defaultValue={toDate}
              className="w-full rounded-md border border-ag-line bg-ag-card px-2 py-1.5 text-sm outline-none focus:border-ag-accent"
            />
          </label>
          <div className="flex items-end">
            <button
              type="submit"
              className="rounded-md border border-ag-accent/50 bg-ag-accent/10 px-3 py-1.5 text-xs font-semibold text-ag-accent hover:bg-ag-accent/20"
            >
              Apply Filters
            </button>
          </div>
        </form>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Issue Total</div>
          <div className="mt-2 text-2xl font-semibold">{issueData.total}</div>
        </Card>
        <Card>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Latest Fail Count</div>
          <div className="mt-2 text-2xl font-semibold">{latest?.fail_count ?? "-"}</div>
        </Card>
        <Card>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Latest Warn Count</div>
          <div className="mt-2 text-2xl font-semibold">{latest?.warn_count ?? "-"}</div>
        </Card>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_420px]">
        <Card>
          <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Issue Feed</div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-[13px]">
              <thead className="border-b border-ag-line text-[11px] uppercase tracking-wide text-ag-mute">
                <tr>
                  <th className="px-2 py-1">id</th>
                  <th className="px-2 py-1">source</th>
                  <th className="px-2 py-1">rule_code</th>
                  <th className="px-2 py-1">severity</th>
                  <th className="px-2 py-1">batch_id</th>
                </tr>
              </thead>
              <tbody>
                {issueData.items.slice(0, 20).map((issue) => (
                  <tr key={issue.id} className="border-b border-ag-line/70">
                    <td className="px-2 py-1.5 font-mono text-xs">{issue.id}</td>
                    <td className="px-2 py-1.5">{issue.source}</td>
                    <td className="px-2 py-1.5 text-ag-mute">{issue.rule_code}</td>
                    <td className="px-2 py-1.5">{issue.severity}</td>
                    <td className="px-2 py-1.5 font-mono text-xs text-ag-mute">{issue.batch_id ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card>
          <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Daily Summary</div>
          <ul className="space-y-2">
            {summaryData.items.slice(0, 10).map((row) => (
              <li key={`${row.summary_date}:${row.source}`} className="rounded border border-ag-line bg-ag-panel/70 p-2 text-xs">
                <div className="font-semibold">
                  {row.summary_date} / {row.source}
                </div>
                <div className="mt-1 text-ag-mute">
                  pass {row.pass_count} | warn {row.warn_count} | fail {row.fail_count}
                </div>
              </li>
            ))}
            {summaryData.items.length === 0 ? <li className="text-xs text-ag-mute">No summary rows yet.</li> : null}
          </ul>
        </Card>
      </div>
    </AppShell>
  );
}
