import { CompanyCard } from "@/components/company-card";
import { getCompany } from "@/lib/api";

export default async function CompanyPage({
  params,
}: {
  params: Promise<{ corpCode: string }>;
}) {
  const { corpCode } = await params;
  const company = await getCompany(corpCode);
  return (
    <CompanyCard
      corpCode={company.corp_code}
      corpName={company.corp_name}
      marketCap={company.market_cap}
    />
  );
}
