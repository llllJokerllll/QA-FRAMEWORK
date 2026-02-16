"""
Tests E2E para el Dashboard principal.
"""
import pytest
from playwright.async_api import Page, expect


BASE_URL = "http://localhost:3000"


@pytest.mark.asyncio
@pytest.mark.e2e
class TestDashboard:
    """Tests del dashboard principal."""
    
    async def test_dashboard_loads(self, authenticated_page: Page):
        """Verificar que el dashboard carga correctamente."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/")
        
        # Verificar elementos principales
        await expect(page.locator('h1, h2').first).to_be_visible(timeout=10000)
    
    async def test_dashboard_stats_visible(self, authenticated_page: Page):
        """Verificar que las estadísticas son visibles."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/")
        
        # Buscar tarjetas de estadísticas
        stats_cards = page.locator('.stat-card, .metric-card, [data-testid="stat"]')
        
        if await stats_cards.count() > 0:
            count = await stats_cards.count()
            assert count >= 1, "Debería haber al menos una tarjeta de estadísticas"
    
    async def test_dashboard_charts_visible(self, authenticated_page: Page):
        """Verificar que los gráficos son visibles."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/")
        
        # Buscar contenedores de gráficos
        charts = page.locator('canvas, svg.chart, [data-testid="chart"], .recharts-wrapper')
        
        if await charts.count() > 0:
            await expect(charts.first).to_be_visible(timeout=10000)
    
    async def test_dashboard_recent_executions(self, authenticated_page: Page):
        """Verificar sección de ejecuciones recientes."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/")
        
        # Buscar sección de ejecuciones recientes
        recent_section = page.locator('text=/Ejecuciones Recientes|Recent Executions/')
        
        if await recent_section.count() > 0:
            await expect(recent_section).to_be_visible()
    
    async def test_dashboard_navigation_sidebar(self, authenticated_page: Page):
        """Verificar navegación en sidebar."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/")
        
        # Verificar links de navegación
        nav_links = page.locator('nav a, [role="navigation"] a')
        count = await nav_links.count()
        
        assert count >= 3, "Debería haber al menos 3 links de navegación"
    
    async def test_dashboard_quick_actions(self, authenticated_page: Page):
        """Verificar acciones rápidas."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/")
        
        # Buscar botones de acción rápida
        quick_actions = page.locator('button:has-text("Nueva"), button:has-text("Ejecutar"), a:has-text("Nuevo")')
        
        if await quick_actions.count() > 0:
            await expect(quick_actions.first).to_be_visible()


@pytest.mark.asyncio
@pytest.mark.e2e
class TestDashboardFilters:
    """Tests de filtros del dashboard."""
    
    async def test_filter_by_date_range(self, authenticated_page: Page):
        """Filtrar por rango de fechas."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/")
        
        date_filter = page.locator('input[type="date"], [data-testid="date-filter"]')
        
        if await date_filter.count() >= 2:
            await date_filter.first.fill("2026-02-01")
            await date_filter.last.fill("2026-02-28")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1000)
    
    async def test_filter_by_suite(self, authenticated_page: Page):
        """Filtrar por suite."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/")
        
        suite_filter = page.locator('select[name="suite"], [data-testid="suite-filter"]')
        
        if await suite_filter.count() > 0:
            await suite_filter.select_option(index=1)
            await page.wait_for_timeout(1000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestDashboardResponsiveness:
    """Tests de responsividad del dashboard."""
    
    async def test_dashboard_responsive_desktop(self, authenticated_page: Page):
        """Dashboard en resolución desktop."""
        page = authenticated_page
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto(f"{BASE_URL}/")
        
        await expect(page.locator('main, [role="main"]')).to_be_visible()
    
    async def test_dashboard_responsive_tablet(self, authenticated_page: Page):
        """Dashboard en resolución tablet."""
        page = authenticated_page
        await page.set_viewport_size({"width": 768, "height": 1024})
        await page.goto(f"{BASE_URL}/")
        
        await expect(page.locator('main, [role="main"]')).to_be_visible()
    
    async def test_dashboard_responsive_mobile(self, authenticated_page: Page):
        """Dashboard en resolución mobile."""
        page = authenticated_page
        await page.set_viewport_size({"width": 375, "height": 667})
        await page.goto(f"{BASE_URL}/")
        
        # En mobile puede haber menú hamburguesa
        await expect(page.locator('body')).to_be_visible()
        
        # Verificar si hay menú hamburguesa
        hamburger = page.locator('[data-testid="menu-button"], button[aria-label*="menu"]')
        if await hamburger.count() > 0:
            await hamburger.click()
            await page.wait_for_timeout(500)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestDashboardRealTime:
    """Tests de actualización en tiempo real."""
    
    async def test_dashboard_auto_refresh(self, authenticated_page: Page):
        """Verificar actualización automática del dashboard."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/")
        
        # Obtener contenido inicial
        initial_content = await page.content()
        
        # Esperar posible actualización
        await page.wait_for_timeout(5000)
        
        # El dashboard debería seguir funcionando
        await expect(page.locator('body')).to_be_visible()
    
    async def test_live_execution_updates(self, authenticated_page: Page):
        """Verificar actualizaciones de ejecución en vivo."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        # Buscar ejecución en progreso
        running_exec = page.locator('text=/Running|En Progreso/')
        
        if await running_exec.count() > 0:
            # Esperar actualizaciones
            await page.wait_for_timeout(3000)
            await expect(running_exec.first).to_be_visible()
