"""
Tests E2E para autenticación.
"""
import pytest
from playwright.async_api import Page, expect


BASE_URL = "http://localhost:3000"


@pytest.mark.asyncio
@pytest.mark.e2e
class TestLogin:
    """Tests de la página de login."""
    
    async def test_login_page_loads(self, page: Page):
        """Verificar que la página de login carga correctamente."""
        await page.goto(f"{BASE_URL}/login")
        
        # Verificar elementos principales
        await expect(page.locator('input[name="email"]')).to_be_visible()
        await expect(page.locator('input[name="password"]')).to_be_visible()
        await expect(page.locator('button[type="submit"]')).to_be_visible()
    
    async def test_login_with_valid_credentials(self, page: Page):
        """Login con credenciales válidas."""
        await page.goto(f"{BASE_URL}/login")
        
        # Completar formulario
        await page.fill('input[name="email"]', 'test@example.com')
        await page.fill('input[name="password"]', 'testpassword123')
        await page.click('button[type="submit"]')
        
        # Verificar redirección al dashboard
        await page.wait_for_url(f"{BASE_URL}/", timeout=10000)
        await expect(page).to_have_url(f"{BASE_URL}/")
    
    async def test_login_with_invalid_credentials(self, page: Page):
        """Login con credenciales inválidas muestra error."""
        await page.goto(f"{BASE_URL}/login")
        
        # Completar formulario con credenciales inválidas
        await page.fill('input[name="email"]', 'invalid@example.com')
        await page.fill('input[name="password"]', 'wrongpassword')
        await page.click('button[type="submit"]')
        
        # Verificar mensaje de error
        await expect(page.locator('.error-message, [role="alert"]')).to_be_visible(timeout=5000)
        
        # Verificar que sigue en la página de login
        await expect(page).to_have_url(f"{BASE_URL}/login")
    
    async def test_login_validation_empty_fields(self, page: Page):
        """Verificar validación de campos vacíos."""
        await page.goto(f"{BASE_URL}/login")
        
        # Intentar submit sin completar campos
        await page.click('button[type="submit"]')
        
        # Verificar mensajes de validación
        email_input = page.locator('input[name="email"]')
        password_input = page.locator('input[name="password"]')
        
        # Los campos deben ser requeridos (HTML5 validation o custom)
        await expect(email_input).to_have_attribute("required", "")
        await expect(password_input).to_have_attribute("required", "")
    
    async def test_logout(self, authenticated_page: Page):
        """Verificar logout cierra sesión correctamente."""
        page = authenticated_page
        
        # Buscar y hacer click en botón de logout
        logout_button = page.locator('button:has-text("Logout"), button:has-text("Cerrar sesión"), [data-testid="logout"]')
        
        if await logout_button.count() > 0:
            await logout_button.click()
            await page.wait_for_url(f"{BASE_URL}/login", timeout=5000)
            await expect(page).to_have_url(f"{BASE_URL}/login")
    
    async def test_protected_route_redirects_to_login(self, page: Page):
        """Verificar que rutas protegidas redirigen a login si no hay sesión."""
        # Intentar acceder a página protegida sin autenticación
        await page.goto(f"{BASE_URL}/suites")
        
        # Debe redirigir a login
        await page.wait_for_url(f"{BASE_URL}/login*", timeout=5000)
        await expect(page).to_have_url(f"{BASE_URL}/login")


@pytest.mark.asyncio
@pytest.mark.e2e
class TestLoginUI:
    """Tests de UI de la página de login."""
    
    async def test_login_form_responsive(self, page: Page):
        """Verificar que el formulario es responsive."""
        # Desktop
        await page.set_viewport_size({"width": 1280, "height": 720})
        await page.goto(f"{BASE_URL}/login")
        await expect(page.locator('form')).to_be_visible()
        
        # Tablet
        await page.set_viewport_size({"width": 768, "height": 1024})
        await expect(page.locator('form')).to_be_visible()
        
        # Mobile
        await page.set_viewport_size({"width": 375, "height": 667})
        await expect(page.locator('form')).to_be_visible()
    
    async def test_password_field_masked(self, page: Page):
        """Verificar que el campo de password está enmascarado."""
        await page.goto(f"{BASE_URL}/login")
        
        password_input = page.locator('input[name="password"]')
        await expect(password_input).to_have_attribute("type", "password")
