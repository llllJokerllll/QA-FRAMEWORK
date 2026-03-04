import { test, expect } from '@playwright/test';

const FRONTEND_URL = 'https://frontend-phi-three-52.vercel.app';

test('Debug: Verificar login manual paso a paso', async ({ page }) => {
  // Ir a la página de login
  console.log('📍 Navegando a /login...');
  await page.goto(`${FRONTEND_URL}/login`);
  await page.waitForLoadState('networkidle');
  
  // Tomar screenshot inicial
  await page.screenshot({ path: 'test-results/01-login-page.png' });
  console.log('📸 Screenshot: 01-login-page.png');
  
  // Verificar que la página cargó
  const title = await page.title();
  console.log(`📌 Título de la página: ${title}`);
  
  // Esperar a que los inputs estén disponibles
  await page.waitForTimeout(2000);
  
  // Buscar inputs
  const inputs = await page.locator('input').count();
  console.log(`📌 Inputs encontrados: ${inputs}`);
  
  // Llenar username
  console.log('⌨️ Llenando username: Joker');
  await page.locator('input').nth(0).fill('Joker');
  
  // Llenar password
  console.log('⌨️ Llenando password: Joker123!');
  await page.locator('input').nth(1).fill('Joker123!');
  
  // Tomar screenshot con datos
  await page.screenshot({ path: 'test-results/02-form-filled.png' });
  console.log('📸 Screenshot: 02-form-filled.png');
  
  // Click en login
  console.log('🖱️ Click en botón Login...');
  await page.click('button:has-text("Login")');
  
  // Esperar respuesta
  console.log('⏳ Esperando respuesta...');
  await page.waitForTimeout(5000);
  
  // Tomar screenshot después del click
  await page.screenshot({ path: 'test-results/03-after-click.png' });
  console.log('📸 Screenshot: 03-after-click.png');
  
  // Verificar URL actual
  const currentUrl = page.url();
  console.log(`📌 URL actual: ${currentUrl}`);
  
  // Verificar si hay mensaje de error
  const errorVisible = await page.locator('text=Invalid').isVisible().catch(() => false);
  if (errorVisible) {
    const errorText = await page.locator('text=Invalid').textContent();
    console.log(`❌ Error visible: ${errorText}`);
  }
  
  // Verificar si hay toast/notification
  const toastVisible = await page.locator('[role="alert"]').isVisible().catch(() => false);
  if (toastVisible) {
    const toastText = await page.locator('[role="alert"]').textContent();
    console.log(`🔔 Toast: ${toastText}`);
  }
  
  // Verificar si redirigió
  if (currentUrl.includes('/login')) {
    console.log('❌ Aún en página de login - login falló');
  } else {
    console.log('✅ Redirigió a: ' + currentUrl + ' - login exitoso');
  }
  
  // Screenshot final
  await page.screenshot({ path: 'test-results/04-final.png', fullPage: true });
  console.log('📸 Screenshot: 04-final.png');
});
