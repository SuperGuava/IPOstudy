import { AppShell } from "@/components/app-shell";
import { CompanyCard } from "@/components/company-card";
import { getCompany } from "@/lib/api";

function formatNumber(value?: number): string {
  if (typeof value !== "number") {
    return "-";
  }
  return value.toLocaleString("en-US");
}

export default async function CompanyPage({
  params,
}: {
  params: Promise<{ corpCode: string }>;
}) {
  const { corpCode } = await params;
  const company = await getCompany(corpCode);
  return (
    <AppShell title="Company Snapshot" subtitle="Unified profile and market snapshot">
      <CompanyCard
        corpCode={company.corp_code}
        corpName={company.profile?.corp_name ?? "unknown"}
        marketCap={formatNumber(company.market?.market_cap)}
      />
    </AppShell>
  );
}
