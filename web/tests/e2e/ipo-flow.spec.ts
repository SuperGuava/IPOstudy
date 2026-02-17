import { expect, test } from "@playwright/test";

test("navigate ipo board to detail", async ({ page }) => {
  await page.goto("/ipo");
  await expect(page.getByTestId("app-shell")).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Primary" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "IPO Pipeline" })).toBeVisible();
  await page.locator("a[href^='/ipo/']").first().click();
  await expect(page).toHaveURL(/\/ipo\/.+/);
  await expect(page.getByText("Entity detail", { exact: true })).toBeVisible();
});

test("dashboard and quality render live metric panels", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByText("Pipeline Size", { exact: true })).toBeVisible();
  await expect(page.getByText("Stage Mix", { exact: true })).toBeVisible();
  await expect(page.getByText("Fail Rate Trend", { exact: true })).toBeVisible();

  await page.getByRole("link", { name: "Quality" }).click();
  await expect(page).toHaveURL(/\/quality/);
  await expect(page.getByRole("heading", { name: "Quality" })).toBeVisible();
  await expect(page.getByText("Issue Feed", { exact: true })).toBeVisible();
  const filterForm = page.locator("form").first();
  await expect(filterForm.locator("input[name='source']")).toBeVisible();
  await expect(filterForm.locator("select[name='severity']")).toBeVisible();
  await expect(filterForm.locator("input[name='from']")).toBeVisible();
  await expect(filterForm.locator("input[name='to']")).toBeVisible();
  await expect(page.getByRole("button", { name: "Apply Filters" })).toBeVisible();
});

test("company explorer renders beginner-friendly analysis surface", async ({ page }) => {
  await page.goto("/explorer");
  await expect(page.getByRole("heading", { name: "Company Explorer" })).toBeVisible();
  await expect(page.getByText("Beginner Summary", { exact: true })).toBeVisible();
  await expect(page.getByText("Analysis Templates", { exact: true })).toBeVisible();
  await expect(page.getByText("Compare Snapshot", { exact: true })).toBeVisible();
  await expect(page.getByText("Company List", { exact: true })).toBeVisible();
});
