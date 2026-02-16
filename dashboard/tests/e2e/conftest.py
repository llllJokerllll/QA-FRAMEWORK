"""
Configuración de fixtures para tests E2E con Playwright.
"""
import pytest
import asyncio
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from typing import AsyncGenerator


# Configuración base
BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:8000"
HEADLESS = True


@pytest.fixture(scope="session")
def event_loop():
    """Crear event loop para tests async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def browser() -> AsyncGenerator[Browser, None]:
    """Browser compartido para todos los tests."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        yield browser
        await browser.close()


@pytest.fixture
async def context(browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """Contexto aislado para cada test."""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="es-ES"
    )
    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext) -> AsyncGenerator[Page, None]:
    """Página nueva para cada test."""
    page = await context.new_page()
    # Capturar errores de consola
    page.on("console", lambda msg: print(f"Console: {msg.text}"))
    page.on("pageerror", lambda err: print(f"Error: {err}"))
    yield page
    await page.close()


@pytest.fixture
async def authenticated_page(page: Page) -> Page:
    """Página con usuario autenticado."""
    # Navegar a login
    await page.goto(f"{BASE_URL}/login")
    
    # Completar formulario de login
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'testpassword123')
    await page.click('button[type="submit"]')
    
    # Esperar redirección al dashboard
    await page.wait_for_url(f"{BASE_URL}/", timeout=5000)
    
    return page


# Helpers para tests
class TestHelpers:
    """Utilidades para tests E2E."""
    
    @staticmethod
    async def wait_for_api_response(page: Page, url_pattern: str, timeout: int = 5000):
        """Esperar respuesta de API específica."""
        async with page.expect_response(url_pattern, timeout=timeout) as response:
            return await response.value
    
    @staticmethod
    async def take_screenshot_on_failure(page: Page, test_name: str):
        """Capturar screenshot en caso de fallo."""
        await page.screenshot(path=f"tests/e2e/screenshots/{test_name}_failure.png")
    
    @staticmethod
    async def login_as(page: Page, email: str, password: str):
        """Login con credenciales específicas."""
        await page.goto(f"{BASE_URL}/login")
        await page.fill('input[name="email"]', email)
        await page.fill('input[name="password"]', password)
        await page.click('button[type="submit"]')
        await page.wait_for_url(f"{BASE_URL}/", timeout=5000)


@pytest.fixture
def helpers():
    """Fixture de helpers."""
    return TestHelpers()
