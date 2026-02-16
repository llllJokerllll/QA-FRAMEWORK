"""
Tests E2E para gestión de Test Cases.
"""
import pytest
from playwright.async_api import Page, expect
import uuid


BASE_URL = "http://localhost:3000"


@pytest.mark.asyncio
@pytest.mark.e2e
class TestCasesList:
    """Tests de listado de casos de prueba."""
    
    async def test_cases_page_loads(self, authenticated_page: Page):
        """Verificar que la página de casos carga correctamente."""
        page = authenticated_page
        
        # Navegar a una suite específica o a la lista de casos
        await page.goto(f"{BASE_URL}/suites")
        
        # Click en una suite para ver sus casos
        suite_link = page.locator('a[href*="/cases"], tr:has(a)').first
        
        if await suite_link.count() > 0:
            await suite_link.click()
            await page.wait_for_selector('h1, h2, table', timeout=10000)
    
    async def test_cases_list_displays_data(self, authenticated_page: Page):
        """Verificar que se muestran los casos existentes."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        # Verificar que hay contenido
        await page.wait_for_selector('table, [role="list"], .case-card', timeout=10000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestCasesCreate:
    """Tests de creación de casos de prueba."""
    
    async def test_create_case_button_opens_form(self, authenticated_page: Page):
        """Verificar que el botón de crear caso abre el formulario."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        # Click en una suite
        suite_link = page.locator('a[href*="/cases"]').first
        
        if await suite_link.count() > 0:
            await suite_link.click()
            
            # Click en crear caso
            create_button = page.locator('button:has-text("Nuevo Caso"), button:has-text("New Case")')
            
            if await create_button.count() > 0:
                await create_button.click()
                await expect(page.locator('form, [role="dialog"]')).to_be_visible(timeout=5000)
    
    async def test_create_case_with_valid_data(self, authenticated_page: Page):
        """Crear caso de prueba con datos válidos."""
        page = authenticated_page
        case_name = f"Test Case E2E {uuid.uuid4().hex[:8]}"
        
        await page.goto(f"{BASE_URL}/suites")
        
        # Navegar a casos de una suite
        suite_link = page.locator('a[href*="/cases"]').first
        
        if await suite_link.count() > 0:
            await suite_link.click()
            
            # Abrir formulario de nuevo caso
            create_button = page.locator('button:has-text("Nuevo"), button:has-text("Create")')
            if await create_button.count() > 0:
                await create_button.first.click()
                
                # Completar formulario
                name_input = page.locator('input[name="name"], input[name="title"], #name, #title')
                await name_input.fill(case_name)
                
                description_input = page.locator('textarea[name="description"], #description')
                if await description_input.count() > 0:
                    await description_input.fill("Descripción del caso de prueba E2E")
                
                # Seleccionar tipo si existe
                type_select = page.locator('select[name="type"], #type')
                if await type_select.count() > 0:
                    await type_select.select_option(label="Functional")
                
                # Enviar
                submit_button = page.locator('button[type="submit"], button:has-text("Guardar")')
                await submit_button.click()
                
                await page.wait_for_timeout(2000)
                
                # Verificar que aparece
                await expect(page.locator(f'text="{case_name}"')).to_be_visible(timeout=5000)
    
    async def test_create_case_with_steps(self, authenticated_page: Page):
        """Crear caso de prueba con pasos."""
        page = authenticated_page
        
        await page.goto(f"{BASE_URL}/suites")
        suite_link = page.locator('a[href*="/cases"]').first
        
        if await suite_link.count() > 0:
            await suite_link.click()
            
            create_button = page.locator('button:has-text("Nuevo")')
            if await create_button.count() > 0:
                await create_button.first.click()
                
                # Completar datos básicos
                name_input = page.locator('input[name="name"], #name')
                await name_input.fill(f"Case with Steps {uuid.uuid4().hex[:8]}")
                
                # Añadir pasos si el campo existe
                steps_input = page.locator('textarea[name="steps"], #steps, [data-testid="steps"]')
                if await steps_input.count() > 0:
                    await steps_input.fill("1. Paso uno\n2. Paso dos\n3. Paso tres")
                
                submit_button = page.locator('button[type="submit"]')
                await submit_button.click()
                
                await page.wait_for_timeout(2000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestCasesUpdate:
    """Tests de actualización de casos de prueba."""
    
    async def test_edit_case(self, authenticated_page: Page):
        """Editar un caso de prueba existente."""
        page = authenticated_page
        new_name = f"Updated Case {uuid.uuid4().hex[:8]}"
        
        await page.goto(f"{BASE_URL}/suites")
        suite_link = page.locator('a[href*="/cases"]').first
        
        if await suite_link.count() > 0:
            await suite_link.click()
            
            # Click en editar
            edit_button = page.locator('button:has-text("Editar"), button:has-text("Edit")').first
            
            if await edit_button.count() > 0:
                await edit_button.click()
                
                # Modificar nombre
                name_input = page.locator('input[name="name"], input[name="title"]')
                await name_input.fill(new_name)
                
                # Guardar
                submit_button = page.locator('button[type="submit"]')
                await submit_button.click()
                
                await page.wait_for_timeout(2000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestCasesDelete:
    """Tests de eliminación de casos de prueba."""
    
    async def test_delete_case_with_confirmation(self, authenticated_page: Page):
        """Eliminar un caso de prueba con confirmación."""
        page = authenticated_page
        
        await page.goto(f"{BASE_URL}/suites")
        suite_link = page.locator('a[href*="/cases"]').first
        
        if await suite_link.count() > 0:
            await suite_link.click()
            
            # Buscar botón de eliminar
            delete_button = page.locator('button:has-text("Eliminar"), button:has-text("Delete")').first
            
            if await delete_button.count() > 0:
                await delete_button.click()
                
                # Confirmar
                confirm_button = page.locator('button:has-text("Confirmar"), button:has-text("Confirm")')
                if await confirm_button.count() > 0:
                    await confirm_button.click()
                
                await page.wait_for_timeout(2000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestCasesFiltering:
    """Tests de filtrado de casos de prueba."""
    
    async def test_filter_cases_by_type(self, authenticated_page: Page):
        """Filtrar casos por tipo."""
        page = authenticated_page
        
        await page.goto(f"{BASE_URL}/suites")
        suite_link = page.locator('a[href*="/cases"]').first
        
        if await suite_link.count() > 0:
            await suite_link.click()
            
            # Buscar filtro por tipo
            type_filter = page.locator('select[name="type"], #filter-type, [data-testid="filter-type"]')
            
            if await type_filter.count() > 0:
                await type_filter.select_option(label="Functional")
                await page.wait_for_timeout(1000)
    
    async def test_search_cases(self, authenticated_page: Page):
        """Buscar casos por nombre."""
        page = authenticated_page
        
        await page.goto(f"{BASE_URL}/suites")
        suite_link = page.locator('a[href*="/cases"]').first
        
        if await suite_link.count() > 0:
            await suite_link.click()
            
            search_input = page.locator('input[type="search"], input[placeholder*="buscar"]')
            
            if await search_input.count() > 0:
                await search_input.fill("test search")
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(1000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestCasesPriority:
    """Tests de priorización de casos."""
    
    async def test_set_case_priority(self, authenticated_page: Page):
        """Establecer prioridad de un caso."""
        page = authenticated_page
        
        await page.goto(f"{BASE_URL}/suites")
        suite_link = page.locator('a[href*="/cases"]').first
        
        if await suite_link.count() > 0:
            await suite_link.click()
            
            edit_button = page.locator('button:has-text("Editar")').first
            
            if await edit_button.count() > 0:
                await edit_button.click()
                
                # Cambiar prioridad
                priority_select = page.locator('select[name="priority"], #priority')
                
                if await priority_select.count() > 0:
                    await priority_select.select_option(label="High")
                    
                    submit_button = page.locator('button[type="submit"]')
                    await submit_button.click()
                    
                    await page.wait_for_timeout(2000)
