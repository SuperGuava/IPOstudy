import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { getIpoPipeline, getQualityIssues, getQualitySummary } from "@/lib/api";

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function stageKey(stage: string): "offering" | "prelisting" | "listed" | "other" {
  const lowered = stage.toLowerCase();
  if (lowered.includes("offer")) return "offering";
  if (lowered.includes("pre")) return "prelisting";
  if (lowered.includes("list")) return "listed";
  return "other";
}

export default async function Home() {
  const [pipelineData, summaryData, issueData] = await Promise.all([
    getIpoPipeline().catch(() => ({ items: [], total: 0 })),
    getQualitySummary().catch(() => ({ items: [], total: 0 })),
    getQualityIssues().catch(() => ({ items: [], total: 0 })),
  ]);

  const offeringCount = pipelineData.items.filter((item) => item.stage.toLowerCase().includes("offer")).length;
  const latestSummary = summaryData.items[0];
  const latestIssues = issueData.items.slice(0, 5);
  const stageMix = pipelineData.items.reduce(
    (acc, item) => {
      acc[stageKey(item.stage)] += 1;
      return acc;
    },
    { offering: 0, prelisting: 0, listed: 0, other: 0 },
  );
  const mixTotal = Math.max(1, pipelineData.items.length);
  const summaryTrend = [...summaryData.items].slice(0, 7).reverse();

  return (
    <AppShell title="Dashboard" subtitle="Internal strategy workspace for IPO intelligence">
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Pipeline Size</div>
          <div className="mt-2 text-2xl font-semibold">{pipelineData.total}</div>
        </Card>
        <Card>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Offering Count</div>
          <div className="mt-2 text-2xl font-semibold">{offeringCount}</div>
        </Card>
        <Card>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Latest Fail Rate</div>
          <div className="mt-2 text-2xl font-semibold">{latestSummary ? formatPercent(latestSummary.fail_rate) : "-"}</div>
        </Card>
        <Card>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Issue Backlog</div>
          <div className="mt-2 text-2xl font-semibold">{issueData.total}</div>
        </Card>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_360px]">
        <Card>
          <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Pipeline Feed</div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-[13px]">
              <thead className="border-b border-ag-line text-[11px] uppercase tracking-wide text-ag-mute">
                <tr>
                  <th className="px-2 py-1">corp_name</th>
                  <th className="px-2 py-1">stage</th>
                  <th className="px-2 py-1">listing_date</th>
                </tr>
              </thead>
              <tbody>
                {pipelineData.items.slice(0, 8).map((item) => (
                  <tr key={item.pipeline_id} className="border-b border-ag-line/70">
                    <td className="px-2 py-1.5">{item.corp_name}</td>
                    <td className="px-2 py-1.5 text-ag-mute">{item.stage}</td>
                    <td className="px-2 py-1.5 text-ag-mute">{item.listing_date ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card>
          <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Recent Issues</div>
          <ul className="space-y-2">
            {latestIssues.length > 0 ? (
              latestIssues.map((issue) => (
                <li key={issue.id} className="rounded border border-ag-line bg-ag-panel/70 p-2 text-xs">
                  <div className="font-semibold">
                    [{issue.severity}] {issue.rule_code}
                  </div>
                  <div className="mt-1 text-ag-mute">{issue.message}</div>
                </li>
              ))
            ) : (
              <li className="text-xs text-ag-mute">No issues observed yet.</li>
            )}
          </ul>
        </Card>
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        <Card>
          <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Stage Mix</div>
          <div className="space-y-2">
            {Object.entries(stageMix).map(([key, value]) => {
              const width = Math.max(8, Math.round((value / mixTotal) * 100));
              return (
                <div key={key}>
                  <div className="mb-1 flex items-center justify-between text-xs">
                    <span className="uppercase text-ag-mute">{key}</span>
                    <span>{value}</span>
                  </div>
                  <div className="h-2 rounded bg-ag-panel">
                    <div className="h-2 rounded bg-ag-accent" style={{ width: `${width}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>

        <Card>
          <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Fail Rate Trend</div>
          <div className="space-y-2">
            {summaryTrend.length > 0 ? (
              summaryTrend.map((row) => {
                const width = Math.max(8, Math.round(row.fail_rate * 100));
                return (
                  <div key={`${row.summary_date}-${row.source}`}>
                    <div className="mb-1 flex items-center justify-between text-xs">
                      <span className="font-mono text-ag-mute">{row.summary_date}</span>
                      <span>{formatPercent(row.fail_rate)}</span>
                    </div>
                    <div className="h-2 rounded bg-ag-panel">
                      <div className="h-2 rounded bg-ag-fail" style={{ width: `${width}%` }} />
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-xs text-ag-mute">No summary history yet.</div>
            )}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
