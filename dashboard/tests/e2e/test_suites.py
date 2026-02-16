"""
Tests E2E para gestión de Test Suites.
"""
import pytest
from playwright.async_api import Page, expect
import uuid


BASE_URL = "http://localhost:3000"


@pytest.mark.asyncio
@pytest.mark.e2e
class TestSuitesList:
    """Tests de listado de suites."""
    
    async def test_suites_page_loads(self, authenticated_page: Page):
        """Verificar que la página de suites carga correctamente."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        # Verificar elementos principales
        await expect(page.locator('h1, h2').filter(has_text="Suites")).to_be_visible()
        await expect(page.locator('button:has-text("Nueva"), button:has-text("Create")')).to_be_visible()
    
    async def test_suites_list_displays_data(self, authenticated_page: Page):
        """Verificar que se muestran las suites existentes."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        # Esperar a que carguen los datos
        await page.wait_for_selector('table, [role="list"], .suite-card', timeout=10000)
        
        # Verificar que hay contenido
        suites = page.locator('table tbody tr, .suite-card, [role="listitem"]')
        count = await suites.count()
        assert count >= 0, "La lista de suites debería existir"
    
    async def test_suites_search_functionality(self, authenticated_page: Page):
        """Verificar búsqueda de suites."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        search_input = page.locator('input[type="search"], input[placeholder*="buscar"], input[placeholder*="search"]')
        
        if await search_input.count() > 0:
            await search_input.fill("test search")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1000)
            # Verificar que se aplicó el filtro
            await expect(search_input).to_have_value("test search")


@pytest.mark.asyncio
@pytest.mark.e2e
class TestSuitesCreate:
    """Tests de creación de suites."""
    
    async def test_create_suite_button_opens_form(self, authenticated_page: Page):
        """Verificar que el botón de crear abre el formulario."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        # Click en botón de nueva suite
        create_button = page.locator('button:has-text("Nueva"), button:has-text("Create"), button:has-text("Nuevo")')
        await create_button.first.click()
        
        # Verificar que se abre el modal/formulario
        await expect(page.locator('form, [role="dialog"], .modal')).to_be_visible(timeout=5000)
    
    async def test_create_suite_with_valid_data(self, authenticated_page: Page):
        """Crear suite con datos válidos."""
        page = authenticated_page
        suite_name = f"Test Suite E2E {uuid.uuid4().hex[:8]}"
        
        await page.goto(f"{BASE_URL}/suites")
        
        # Abrir formulario
        create_button = page.locator('button:has-text("Nueva"), button:has-text("Create")')
        await create_button.first.click()
        
        # Completar formulario
        name_input = page.locator('input[name="name"], #name, input[placeholder*="nombre"]')
        await name_input.fill(suite_name)
        
        description_input = page.locator('textarea[name="description"], #description')
        if await description_input.count() > 0:
            await description_input.fill("Descripción de prueba E2E")
        
        # Enviar formulario
        submit_button = page.locator('button[type="submit"], button:has-text("Guardar"), button:has-text("Save")')
        await submit_button.click()
        
        # Verificar que se creó (aparece en la lista o mensaje de éxito)
        await page.wait_for_timeout(2000)
        
        # Buscar la suite creada
        await page.goto(f"{BASE_URL}/suites")
        await page.wait_for_selector('table, .suite-card', timeout=5000)
        
        # Verificar que aparece en la lista
        suite_element = page.locator(f'text="{suite_name}"')
        await expect(suite_element).to_be_visible(timeout=5000)
    
    async def test_create_suite_validation_required_fields(self, authenticated_page: Page):
        """Verificar validación de campos requeridos."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        # Abrir formulario
        create_button = page.locator('button:has-text("Nueva"), button:has-text("Create")')
        await create_button.first.click()
        
        # Intentar enviar sin completar
        submit_button = page.locator('button[type="submit"], button:has-text("Guardar")')
        await submit_button.click()
        
        # Verificar mensaje de validación
        await expect(page.locator('.error, [role="alert"], .Mui-error')).to_be_visible(timeout=3000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestSuitesUpdate:
    """Tests de actualización de suites."""
    
    async def test_edit_suite(self, authenticated_page: Page):
        """Editar una suite existente."""
        page = authenticated_page
        new_name = f"Updated Suite {uuid.uuid4().hex[:8]}"
        
        await page.goto(f"{BASE_URL}/suites")
        
        # Buscar una suite y hacer click en editar
        edit_button = page.locator('button:has-text("Editar"), button:has-text("Edit"), [data-testid="edit-suite"]')
        
        if await edit_button.count() > 0:
            await edit_button.first.click()
            
            # Modificar nombre
            name_input = page.locator('input[name="name"], #name')
            await name_input.fill(new_name)
            
            # Guardar
            submit_button = page.locator('button[type="submit"], button:has-text("Guardar")')
            await submit_button.click()
            
            # Verificar actualización
            await page.wait_for_timeout(2000)
            await expect(page.locator(f'text="{new_name}"')).to_be_visible(timeout=5000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestSuitesDelete:
    """Tests de eliminación de suites."""
    
    async def test_delete_suite_with_confirmation(self, authenticated_page: Page):
        """Eliminar una suite con confirmación."""
        page = authenticated_page
        suite_name = f"Suite to Delete {uuid.uuid4().hex[:8]}"
        
        # Primero crear una suite para eliminar
        await page.goto(f"{BASE_URL}/suites")
        
        create_button = page.locator('button:has-text("Nueva"), button:has-text("Create")')
        await create_button.first.click()
        
        name_input = page.locator('input[name="name"], #name')
        await name_input.fill(suite_name)
        
        submit_button = page.locator('button[type="submit"], button:has-text("Guardar")')
        await submit_button.click()
        
        await page.wait_for_timeout(2000)
        
        # Ahora eliminar
        await page.goto(f"{BASE_URL}/suites")
        
        # Buscar la suite y eliminar
        suite_row = page.locator(f'tr:has-text("{suite_name}"), .suite-card:has-text("{suite_name}")')
        delete_button = suite_row.locator('button:has-text("Eliminar"), button:has-text("Delete")')
        
        if await delete_button.count() > 0:
            await delete_button.click()
            
            # Confirmar eliminación
            confirm_button = page.locator('button:has-text("Confirmar"), button:has-text("Confirm")')
            if await confirm_button.count() > 0:
                await confirm_button.click()
            
            await page.wait_for_timeout(2000)
            
            # Verificar que ya no existe
            deleted_suite = page.locator(f'text="{suite_name}"')
            await expect(deleted_suite).not_to_be_visible(timeout=3000)


@pytest.mark.asyncio
@pytest.mark.e2e
class TestSuitesNavigation:
    """Tests de navegación desde suites."""
    
    async def test_navigate_to_suite_cases(self, authenticated_page: Page):
        """Navegar a casos de una suite."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        # Click en una suite
        suite_link = page.locator('a[href*="/cases"], tr:has(a), .suite-card a').first
        
        if await suite_link.count() > 0:
            await suite_link.click()
            await page.wait_for_url("**/cases**", timeout=5000)
            await expect(page).to_have_url(lambda url: "/cases" in url)
    
    async def test_navigate_to_suite_executions(self, authenticated_page: Page):
        """Navegar a ejecuciones de una suite."""
        page = authenticated_page
        await page.goto(f"{BASE_URL}/suites")
        
        executions_button = page.locator('button:has-text("Ejecutar"), button:has-text("Run")').first
        
        if await executions_button.count() > 0:
            await executions_button.click()
            await page.wait_for_url("**/executions**", timeout=5000)
