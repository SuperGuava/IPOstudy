import { expect, test } from "@playwright/test";

test("navigate ipo board to detail", async ({ page }) => {
  await page.goto("/ipo");
  await page.getByRole("link", { name: "알파테크" }).click();
  await expect(page).toHaveURL(/\/ipo\/.+/);
  await expect(page.getByRole("heading", { name: "IPO 상세" })).toBeVisible();
});
