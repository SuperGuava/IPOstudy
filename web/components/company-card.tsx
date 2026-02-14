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
    <article>
      <h1>기업 스냅샷</h1>
      <p>corp_code: {corpCode}</p>
      <p>회사명: {corpName}</p>
      <p>시가총액: {marketCap}</p>
    </article>
  );
}
