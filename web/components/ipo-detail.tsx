import Link from "next/link";

import type { IpoItem } from "@/lib/api";

export function IpoDetail({ item }: { item: IpoItem }) {
  return (
    <article>
      <h1>IPO 상세</h1>
      <p>회사: {item.corp_name}</p>
      <p>단계: {item.stage}</p>
      <p>상장예정일: {item.listing_date}</p>
      <p>
        <Link href={`/company/00126380`}>기업 카드 보기</Link>
      </p>
    </article>
  );
}
