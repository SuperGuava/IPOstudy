import Link from "next/link";

import type { IpoItem } from "@/lib/api";

export function IpoBoard({ items }: { items: IpoItem[] }) {
  return (
    <section>
      <h1>IPO 보드</h1>
      <table>
        <thead>
          <tr>
            <th>회사</th>
            <th>단계</th>
            <th>상장예정일</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.pipeline_id}>
              <td>
                <Link href={`/ipo/${item.pipeline_id}`}>{item.corp_name}</Link>
              </td>
              <td>{item.stage}</td>
              <td>{item.listing_date}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
