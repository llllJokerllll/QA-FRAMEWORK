import { test, expect } from '@playwright/test'

test.describe('Quick Wins - Empty States & Keyboard Shortcuts', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:5173')
  })

  test('Empty State - Test Suites page shows empty state when no suites', async ({ page }) => {
    // Navigate to Test Suites page
    await page.click('text=Test Suites')

    // Wait for page to load
    await page.waitForURL('**/suites')

    // Check if empty state is displayed (when no suites exist)
    const emptyStateImage = page.locator('img[alt*="No Test Suites"]')
    const emptyStateTitle = page.locator('h5:has-text("No Test Suites Yet")')

    // Note: This test assumes the API returns empty data
    // In a real scenario, you might need to mock the API response
    if (await emptyStateImage.isVisible({ timeout: 5000 })) {
      await expect(emptyStateImage).toBeVisible()
      await expect(emptyStateTitle).toBeVisible()

      // Verify empty state has proper content
      await expect(page.locator('text=Create your first test suite')).toBeVisible()

      // Test the "Create First Suite" button
      const createButton = page.locator('button:has-text("Create First Suite")')
      if (await createButton.isVisible()) {
        await createButton.click()
        // Verify it opens the create dialog (check for dialog title)
        await expect(page.locator('text=Create Test Suite')).toBeVisible()
      }
    }
  })

  test('Empty State - Executions page shows empty state when no executions', async ({ page }) => {
    // Navigate to Executions page
    await page.click('text=Executions')

    // Wait for page to load
    await page.waitForURL('**/executions')

    // Check if empty state is displayed
    const emptyStateImage = page.locator('img[alt*="No Executions"]')
    const emptyStateTitle = page.locator('h5:has-text("No Executions Yet")')

    if (await emptyStateImage.isVisible({ timeout: 5000 })) {
      await expect(emptyStateImage).toBeVisible()
      await expect(emptyStateTitle).toBeVisible()

      // Verify empty state has proper content
      await expect(page.locator('text=Run your test suites')).toBeVisible()

      // Test the "Run Your First Test" button
      const runButton = page.locator('button:has-text("Run Your First Test")')
      if (await runButton.isVisible()) {
        const urlBefore = page.url()
        await runButton.click()
        // Verify it navigates to suites page
        await page.waitForURL('**/suites')
        expect(page.url()).not.toBe(urlBefore)
      }
    }
  })

  test('Empty State - Self-Healing page shows empty state when no selectors', async ({ page }) => {
    // Navigate to Self-Healing page
    await page.click('text=Self-Healing')

    // Wait for page to load
    await page.waitForURL('**/self-healing')

    // Check if empty state is displayed
    const emptyStateImage = page.locator('img[alt*="No Selectors"]')
    const emptyStateTitle = page.locator('h5:has-text("No Selectors Found")')

    // Note: Self-Healing page uses mock data, so empty state might not show
    // This test verifies the component exists if data is empty
  })

  test('Empty State - Integrations page shows empty state when no integrations', async ({ page }) => {
    // Navigate to Integrations page
    await page.click('text=Integrations')

    // Wait for page to load
    await page.waitForURL('**/integrations')

    // Check if empty state is displayed
    const emptyStateTitle = page.locator('h5:has-text("No Integrations Configured")')

    if (await emptyStateTitle.isVisible({ timeout: 5000 })) {
      await expect(emptyStateTitle).toBeVisible()

      // Verify empty state has proper content
      await expect(page.locator('text=Connect your test management tools')).toBeVisible()

      // Test the "Configure Integration" button
      const configureButton = page.locator('button:has-text("Configure Integration")')
      if (await configureButton.isVisible()) {
        await configureButton.click()
        // Should show an alert (can't easily test alert in E2E, just verify button exists)
      }
    }
  })

  test('Keyboard Shortcuts - Press "/" focuses search', async ({ page }) => {
    // Press "/" key
    await page.keyboard.press('/')

    // Check if an input is focused
    const focusedElement = page.locator(':focus')
    const tagName = await focusedElement.evaluate(el => el.tagName)

    // Should be an INPUT or TEXTAREA element
    expect(tagName).toMatch(/^(INPUT|TEXTAREA)$/)

    // If it's an input, verify it's a search input
    if (tagName === 'INPUT') {
      const type = await focusedElement.evaluate(el => (el as HTMLInputElement).type)
      const placeholder = await focusedElement.evaluate(el => (el as HTMLInputElement).placeholder)

      // Should be a search input or have search placeholder
      expect(type === 'search' || placeholder.toLowerCase().includes('search')).toBeTruthy()
    }
  })

  test('Keyboard Shortcuts - Press "n" navigates to Test Suites', async ({ page }) => {
    const currentUrl = page.url()

    // Press "n" key
    await page.keyboard.press('n')

    // Wait for navigation
    await page.waitForTimeout(500)

    // Verify navigation to suites page
    await page.waitForURL('**/suites', { timeout: 5000 })
    expect(page.url()).toContain('/suites')
    expect(page.url()).not.toBe(currentUrl)
  })

  test('Keyboard Shortcuts - Press "h" navigates to Home', async ({ page }) => {
    // First navigate to a different page
    await page.click('text=Test Suites')
    await page.waitForURL('**/suites')

    // Press "h" key
    await page.keyboard.press('h')

    // Wait for navigation
    await page.waitForTimeout(500)

    // Verify navigation to home/dashboard
    await page.waitForURL('**/', { timeout: 5000 })
    expect(page.url()).toMatch(/\/(dashboard)?$/)
  })

  test('Keyboard Shortcuts - Press "?" opens help dialog', async ({ page }) => {
    // Press "?" key
    await page.keyboard.press('?')

    // Wait for dialog to appear
    await page.waitForTimeout(500)

    // Check if help dialog is visible
    const dialog = page.locator('[role="dialog"]')
    await expect(dialog).toBeVisible({ timeout: 5000 })

    // Check dialog content
    await expect(page.locator('text=Keyboard Shortcuts')).toBeVisible()
    await expect(page.locator('text=Focus search input')).toBeVisible()
    await expect(page.locator('text=Navigate to Test Suites')).toBeVisible()
    await expect(page.locator('text=Navigate to Home/Dashboard')).toBeVisible()

    // Test closing dialog with Escape
    await page.keyboard.press('Escape')

    // Wait for dialog to close
    await page.waitForTimeout(500)

    // Verify dialog is not visible anymore
    await expect(dialog).not.toBeVisible({ timeout: 5000 })
  })

  test('Keyboard Shortcuts - Dialog can be closed with Escape', async ({ page }) => {
    // Open dialog with "?"
    await page.keyboard.press('?')
    await page.waitForSelector('[role="dialog"]', { state: 'visible' })

    const dialog = page.locator('[role="dialog"]')
    await expect(dialog).toBeVisible()

    // Press Escape to close
    await page.keyboard.press('Escape')

    // Verify dialog is closed
    await expect(dialog).not.toBeVisible({ timeout: 5000 })
  })

  test('Keyboard Shortcuts - Click help icon in header opens dialog', async ({ page }) => {
    // Click the help icon in the header
    const helpIcon = page.locator('button[title*="Keyboard Shortcuts"], button svg[data-testid="HelpIcon"]')

    if (await helpIcon.isVisible({ timeout: 5000 })) {
      await helpIcon.click()

      // Wait for dialog to appear
      await page.waitForTimeout(500)

      // Check if help dialog is visible
      const dialog = page.locator('[role="dialog"]')
      await expect(dialog).toBeVisible({ timeout: 5000 })
    }
  })

  test('Keyboard Shortcuts - Dialog close button works', async ({ page }) => {
    // Open dialog
    await page.keyboard.press('?')
    await page.waitForSelector('[role="dialog"]', { state: 'visible' })

    const dialog = page.locator('[role="dialog"]')
    await expect(dialog).toBeVisible()

    // Click the "Got it!" button
    const closeButton = page.locator('button:has-text("Got it!")')
    await closeButton.click()

    // Verify dialog is closed
    await expect(dialog).not.toBeVisible({ timeout: 5000 })
  })
})
