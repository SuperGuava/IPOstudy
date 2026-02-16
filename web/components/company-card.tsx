import { Card } from "@/components/ui/card";

export function CompanyCard({
  corpCode,
  corpName,
  marketCap,
}: {
  corpCode: string;
  corpName: string;
  marketCap: string;
}) {
  return (
    <Card className="max-w-3xl">
      <h2 className="text-xl font-semibold">Company Snapshot</h2>
      <dl className="mt-3 grid gap-3 text-sm md:grid-cols-3">
        <div>
          <dt className="text-[11px] uppercase tracking-wide text-ag-mute">corp_code</dt>
          <dd className="font-mono text-xs">{corpCode}</dd>
        </div>
        <div>
          <dt className="text-[11px] uppercase tracking-wide text-ag-mute">corp_name</dt>
          <dd>{corpName}</dd>
        </div>
        <div>
          <dt className="text-[11px] uppercase tracking-wide text-ag-mute">market_cap</dt>
          <dd>{marketCap}</dd>
        </div>
      </dl>
    </Card>
  );
}
