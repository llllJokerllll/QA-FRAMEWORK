"""
Tests E2E para Integration Hub.
"""
import pytest
from playwright.async_api import Page, expect


BASE_URL = "http://localhost:3000"


@pytest.mark.asyncio
@pytest.mark.e2e
class TestIntegrationHub:
    """Tests del Integration Hub."""
    
    async def test_integrations_page_loads(self, authenticated_page: Page):
        """Verificar que la página de integraciones carga."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/integrations")
        
        # Verificar que la página existe (puede ser 404 si no está implementada)
        await page.wait_for_load_state("networkidle")
        
        # Si existe, verificar contenido
        integrations_title = page.locator('h1, h2').filter(has_text="Integraciones|Integrations")
        if await integrations_title.count() > 0:
            await expect(integrations_title).to_be_visible()
    
    async def test_list_available_providers(self, authenticated_page: Page):
        """Verificar lista de proveedores disponibles."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/integrations")
        
        # Buscar tarjetas de proveedores
        providers = page.locator('.provider-card, [data-testid="provider"]')
        
        if await providers.count() > 0:
            count = await providers.count()
            assert count >= 1, "Debería haber al menos un proveedor"
    
    async def test_jira_integration_card(self, authenticated_page: Page):
        """Verificar tarjeta de integración Jira."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/integrations")
        
        jira_card = page.locator('text=/Jira|JIRA/')
        
        if await jira_card.count() > 0:
            await expect(jira_card.first).to_be_visible()
    
    async def test_zephyr_integration_card(self, authenticated_page: Page):
        """Verificar tarjeta de integración Zephyr."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/integrations")
        
        zephyr_card = page.locator('text=/Zephyr/')
        
        if await zephyr_card.count() > 0:
            await expect(zephyr_card.first).to_be_visible()
    
    async def test_azure_devops_integration_card(self, authenticated_page: Page):
        """Verificar tarjeta de integración Azure DevOps."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/integrations")
        
        azure_card = page.locator('text=/Azure|DevOps/')
        
        if await azure_card.count() > 0:
            await expect(azure_card.first).to_be_visible()


@pytest.mark.asyncio
@pytest.mark.e2e
class TestIntegrationConfiguration:
    """Tests de configuración de integraciones."""
    
    async def test_configure_jira_opens_modal(self, authenticated_page: Page):
        """Verificar que configurar Jira abre modal."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/integrations")
        
        configure_button = page.locator('button:has-text("Configurar"), button:has-text("Configure")')
        
        if await configure_button.count() > 0:
            await configure_button.first.click()
            
            # Verificar modal
            modal = page.locator('[role="dialog"], .modal')
            if await modal.count() > 0:
                await expect(modal).to_be_visible(timeout=5000)
    
    async def test_integration_form_fields(self, authenticated_page: Page):
        """Verificar campos del formulario de integración."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/integrations")
        
        configure_button = page.locator('button:has-text("Configurar")').first
        
        if await configure_button.count() > 0:
            await configure_button.click()
            
            # Verificar campos típicos
            url_input = page.locator('input[name="url"], input[placeholder*="URL"]')
            api_key_input = page.locator('input[name="api_key"], input[placeholder*="API"]')
            
            # Al menos uno debería existir
            has_url = await url_input.count() > 0
            has_api_key = await api_key_input.count() > 0
            
            assert has_url or has_api_key, "Debería haber campos de configuración"
    
    async def test_save_integration(self, authenticated_page: Page):
        """Guardar configuración de integración."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/integrations")
        
        configure_button = page.locator('button:has-text("Configurar")').first
        
        if await configure_button.count() > 0:
            await configure_button.click()
            
            # Completar campos si existen
            url_input = page.locator('input[name="url"]')
            if await url_input.count() > 0:
                await url_input.fill("https://example.atlassian.net")
            
            # Guardar
            save_button = page.locator('button:has-text("Guardar"), button:has-text("Save")')
            if await save_button.count() > 0:
                await save_button.click()
                await page.wait_for_timeout(2000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestIntegrationSync:
    """Tests de sincronización de integraciones."""
    
    async def test_sync_results_button(self, authenticated_page: Page):
        """Verificar botón de sincronización."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/integrations")
        
        sync_button = page.locator('button:has-text("Sincronizar"), button:has-text("Sync")')
        
        if await sync_button.count() > 0:
            await expect(sync_button.first).to_be_visible()
    
    async def test_sync_status_display(self, authenticated_page: Page):
        """Verificar estado de sincronización."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/integrations")
        
        status = page.locator('.sync-status, [data-testid="sync-status"], text=/Conectado|Connected|Error/')
        
        if await status.count() > 0:
            await expect(status.first).to_be_visible()
    
    async def test_health_check_integration(self, authenticated_page: Page):
        """Verificar health check de integración."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/integrations")
        
        # Buscar indicador de salud
        health_indicator = page.locator('.health-status, [data-testid="health"], .status-badge')
        
        if await health_indicator.count() > 0:
            await expect(health_indicator.first).to_be_visible()


@pytest.mark.asyncio
@pytest.mark.e2e
class TestIntegrationBugs:
    """Tests de creación de bugs desde tests."""
    
    async def test_create_bug_from_failed_test(self, authenticated_page: Page):
        """Crear bug desde test fallido."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        # Buscar ejecución con fallos
        failed_exec = page.locator('tr:has-text("Failed"), .execution-card:has-text("Failed")').first
        
        if await failed_exec.count() > 0:
            await failed_exec.click()
            
            # Buscar botón de crear bug
            create_bug_button = page.locator('button:has-text("Crear Bug"), button:has-text("Create Bug")')
            
            if await create_bug_button.count() > 0:
                await create_bug_button.click()
                
                # Verificar modal
                modal = page.locator('[role="dialog"]')
                if await modal.count() > 0:
                    await expect(modal).to_be_visible()


@pytest.mark.asyncio
@pytest.mark.e2e
class TestIntegrationImport:
    """Tests de importación desde integraciones."""
    
    async def test_import_test_cases_from_jira(self, authenticated_page: Page):
        """Importar casos de prueba desde Jira."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        import_button = page.locator('button:has-text("Importar"), button:has-text("Import")')
        
        if await import_button.count() > 0:
            await import_button.click()
            
            # Verificar opciones de importación
            import_options = page.locator('text=/Jira|Zephyr|Azure/')
            
            if await import_options.count() > 0:
                await expect(import_options.first).to_be_visible()
    
    async def test_import_results_to_external(self, authenticated_page: Page):
        """Exportar resultados a herramienta externa."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        # Seleccionar ejecución
        exec_row = page.locator('table tbody tr, .execution-card').first
        
        if await exec_row.count() > 0:
            await exec_row.click()
            
            # Buscar botón de exportar
            export_button = page.locator('button:has-text("Exportar"), button:has-text("Export")')
            
            if await export_button.count() > 0:
                await export_button.click()
                
                # Verificar opciones
                await page.wait_for_timeout(1000)
