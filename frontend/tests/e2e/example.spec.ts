import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
    await page.goto('/');

    // Expect a title "to contain" a substring.
    // Adjust this expectation based on your actual metadata
    await expect(page).toHaveTitle(/ApplyWise/i);
});
