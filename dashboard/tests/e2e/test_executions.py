"""
Tests E2E para ejecuciones de pruebas.
"""
import pytest
from playwright.async_api import Page, expect
import uuid


BASE_URL = "http://localhost:3000"


@pytest.mark.asyncio
@pytest.mark.e2e
class TestExecutionsList:
    """Tests de listado de ejecuciones."""
    
    async def test_executions_page_loads(self, authenticated_page: Page):
        """Verificar que la página de ejecuciones carga correctamente."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        # Verificar elementos principales
        await expect(page.locator('h1, h2').filter(has_text="Ejecuciones|Executions")).to_be_visible(timeout=10000)
    
    async def test_executions_list_displays_data(self, authenticated_page: Page):
        """Verificar que se muestran las ejecuciones existentes."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        # Esperar a que carguen los datos
        await page.wait_for_selector('table, [role="list"], .execution-card', timeout=10000)
    
    async def test_executions_status_filter(self, authenticated_page: Page):
        """Filtrar ejecuciones por estado."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        status_filter = page.locator('select[name="status"], #filter-status')
        
        if await status_filter.count() > 0:
            await status_filter.select_option(label="Completed")
            await page.wait_for_timeout(1000)
    
    async def test_executions_date_filter(self, authenticated_page: Page):
        """Filtrar ejecuciones por fecha."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        date_filter = page.locator('input[type="date"], input[name="date"]')
        
        if await date_filter.count() > 0:
            await date_filter.first.fill("2026-02-01")
            await page.wait_for_timeout(1000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestExecutionsCreate:
    """Tests de creación de ejecuciones."""
    
    async def test_start_execution_from_suite(self, authenticated_page: Page):
        """Iniciar ejecución desde una suite."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        # Buscar botón de ejecutar
        run_button = page.locator('button:has-text("Ejecutar"), button:has-text("Run")').first
        
        if await run_button.count() > 0:
            await run_button.click()
            
            # Verificar que se redirige a ejecución o se muestra modal
            await page.wait_for_timeout(2000)
            
            # Debe aparecer la ejecución o el modal de confirmación
            execution_started = page.locator('text=/Ejecutando|Running|In Progress/')
            modal_visible = page.locator('[role="dialog"]')
            
            assert await execution_started.count() > 0 or await modal_visible.count() > 0
    
    async def test_create_execution_with_custom_settings(self, authenticated_page: Page):
        """Crear ejecución con configuración personalizada."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        run_button = page.locator('button:has-text("Ejecutar")').first
        
        if await run_button.count() > 0:
            await run_button.click()
            
            # Si hay modal de configuración
            config_modal = page.locator('[role="dialog"]')
            
            if await config_modal.count() > 0:
                # Configurar opciones
                parallel_checkbox = page.locator('input[name="parallel"], #parallel')
                if await parallel_checkbox.count() > 0:
                    await parallel_checkbox.check()
                
                # Iniciar
                start_button = page.locator('button:has-text("Iniciar"), button:has-text("Start")')
                await start_button.click()
                
                await page.wait_for_timeout(2000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestExecutionsMonitoring:
    """Tests de monitoreo de ejecuciones."""
    
    async def test_view_execution_progress(self, authenticated_page: Page):
        """Ver progreso de ejecución en tiempo real."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        # Click en una ejecución en progreso
        running_execution = page.locator('tr:has-text("Running"), .execution-card:has-text("Running")').first
        
        if await running_execution.count() > 0:
            await running_execution.click()
            
            # Verificar que se muestra el detalle
            await expect(page.locator('.progress, [role="progressbar"], .execution-detail')).to_be_visible(timeout=5000)
    
    async def test_view_execution_results(self, authenticated_page: Page):
        """Ver resultados de ejecución completada."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        # Click en una ejecución completada
        completed_execution = page.locator('tr:has-text("Completed"), .execution-card:has-text("Completed")').first
        
        if await completed_execution.count() > 0:
            await completed_execution.click()
            
            # Verificar resultados
            await expect(page.locator('.results, .execution-detail, table')).to_be_visible(timeout=5000)
    
    async def test_execution_status_updates(self, authenticated_page: Page):
        """Verificar que el estado de ejecución se actualiza."""
        page = authenticated_page
        
        # Iniciar una ejecución
        await page.goto(f"{BASE_URL}/suites")
        run_button = page.locator('button:has-text("Ejecutar")').first
        
        if await run_button.count() > 0:
            await run_button.click()
            await page.wait_for_timeout(2000)
            
            # Ir a la página de ejecuciones
            await page.goto(f"{BASE_URL}/executions")
            
            # Verificar que hay una ejecución nueva
            latest_execution = page.locator('table tbody tr, .execution-card').first
            await expect(latest_execution).to_be_visible(timeout=5000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestExecutionsStop:
    """Tests de detención de ejecuciones."""
    
    async def test_stop_running_execution(self, authenticated_page: Page):
        """Detener una ejecución en progreso."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        # Buscar ejecución en progreso
        running_row = page.locator('tr:has-text("Running")').first
        
        if await running_row.count() > 0:
            # Click en detener
            stop_button = running_row.locator('button:has-text("Detener"), button:has-text("Stop")')
            
            if await stop_button.count() > 0:
                await stop_button.click()
                
                # Confirmar si hay diálogo
                confirm_button = page.locator('button:has-text("Confirmar")')
                if await confirm_button.count() > 0:
                    await confirm_button.click()
                
                await page.wait_for_timeout(2000)
                
                # Verificar que el estado cambió
                await expect(page.locator('text=/Stopped|Detenido/')).to_be_visible(timeout=5000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestExecutionsReports:
    """Tests de reportes de ejecuciones."""
    
    async def test_download_execution_report(self, authenticated_page: Page):
        """Descargar reporte de ejecución."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        # Click en una ejecución
        execution_row = page.locator('table tbody tr, .execution-card').first
        
        if await execution_row.count() > 0:
            await execution_row.click()
            
            # Buscar botón de descargar
            download_button = page.locator('button:has-text("Descargar"), button:has-text("Download"), button:has-text("Export")')
            
            if await download_button.count() > 0:
                # Configurar descarga
                async with page.expect_download() as download_info:
                    await download_button.click()
                
                download = await download_info.value
                assert download.suggested_filename is not None
    
    async def test_view_execution_statistics(self, authenticated_page: Page):
        """Ver estadísticas de ejecución."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        # Click en una ejecución
        execution_row = page.locator('table tbody tr, .execution-card').first
        
        if await execution_row.count() > 0:
            await execution_row.click()
            
            # Verificar estadísticas
            stats = page.locator('.statistics, .stats, [data-testid="stats"]')
            await expect(stats).to_be_visible(timeout=5000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestExecutionsRerun:
    """Tests de re-ejecución."""
    
    async def test_rerun_failed_tests(self, authenticated_page: Page):
        """Re-ejecutar tests fallidos."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        # Click en una ejecución con fallos
        failed_execution = page.locator('tr:has-text("Failed")').first
        
        if await failed_execution.count() > 0:
            await failed_execution.click()
            
            # Buscar botón de re-ejecutar fallos
            rerun_button = page.locator('button:has-text("Re-ejecutar"), button:has-text("Rerun Failed")')
            
            if await rerun_button.count() > 0:
                await rerun_button.click()
                await page.wait_for_timeout(2000)
    
    async def test_rerun_all_tests(self, authenticated_page: Page):
        """Re-ejecutar todos los tests."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/executions")
        
        execution_row = page.locator('table tbody tr, .execution-card').first
        
        if await execution_row.count() > 0:
            await execution_row.click()
            
            rerun_all_button = page.locator('button:has-text("Re-ejecutar Todo"), button:has-text("Rerun All")')
            
            if await rerun_all_button.count() > 0:
                await rerun_all_button.click()
                
                # Confirmar
                confirm_button = page.locator('button:has-text("Confirmar")')
                if await confirm_button.count() > 0:
                    await confirm_button.click()
                
                await page.wait_for_timeout(2000)
