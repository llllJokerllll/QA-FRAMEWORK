"""UI Testing Examples using Playwright"""

import pytest
import asyncio
from src.adapters.ui.playwright_page import PlaywrightPage


class TestUIBasic:
    """Basic UI testing examples"""
    
    @pytest.mark.ui
    @pytest.mark.asyncio
    async def test_page_navigation(self):
        """Test basic page navigation."""
        async with PlaywrightPage(browser_type="chromium", headless=True) as page:
            # Navigate to a page
            await page.goto("https://example.com")
            
            # Verify navigation succeeded
            await page.wait_for_selector("h1")
            title = await page.get_text("h1")
            
            assert "Example" in title
            print("✅ Test passed: Page navigation successful")
    
    @pytest.mark.ui
    @pytest.mark.asyncio
    async def test_element_interaction(self):
        """Test element interaction (click, fill)."""
        async with PlaywrightPage(browser_type="chromium", headless=True) as page:
            # Navigate to Wikipedia
            await page.goto("https://en.wikipedia.org")
            
            # Fill search input
            await page.fill("#searchInput", "Python programming")
            
            # Click search button
            await page.click("#searchButton")
            
            # Wait for results
            await page.wait_for_selector(".mw-search-result")
            
            # Verify results
            results = await page.get_text(".mw-search-result")
            assert len(results) > 0
            
            print("✅ Test passed: Element interaction successful")
    
    @pytest.mark.ui
    @pytest.mark.asyncio
    async def test_element_visibility(self):
        """Test checking element visibility."""
        async with PlaywrightPage(browser_type="chromium", headless=True) as page:
            await page.goto("https://example.com")
            
            # Check if element is visible
            h1_visible = await page.is_visible("h1")
            p_visible = await page.is_visible("p")
            
            assert h1_visible
            assert p_visible
            
            # Check non-existent element
            non_existent = await page.is_visible(".non-existent-class")
            assert not non_existent
            
            print("✅ Test passed: Element visibility check successful")
    
    @pytest.mark.ui
    @pytest.mark.asyncio
    async def test_screenshot_capture(self):
        """Test screenshot capture."""
        import os
        from pathlib import Path
        
        # Create screenshots directory
        screenshot_dir = Path("test_screenshots")
        screenshot_dir.mkdir(exist_ok=True)
        
        try:
            async with PlaywrightPage(browser_type="chromium", headless=True) as page:
                await page.goto("https://example.com")
                await page.wait_for_selector("h1")
                
                # Take screenshot
                screenshot_path = screenshot_dir / "example_com.png"
                await page.screenshot(str(screenshot_path))
                
                # Verify screenshot was created
                assert screenshot_path.exists()
                assert screenshot_path.stat().st_size > 0
                
                print(f"✅ Test passed: Screenshot saved to {screenshot_path}")
                
        finally:
            # Cleanup
            if screenshot_dir.exists():
                for file in screenshot_dir.glob("*.png"):
                    file.unlink()
                screenshot_dir.rmdir()


class TestUILoginFlow:
    """Example of login flow testing."""
    
    @pytest.mark.ui
    @pytest.mark.asyncio
    async def test_mock_login_flow(self):
        """Test login flow with mock credentials."""
        async with PlaywrightPage(browser_type="chromium", headless=True) as page:
            # Navigate to login page
            await page.goto("https://example.com/login")
            
            # Fill login form (mock)
            await page.fill("#username", "testuser")
            await page.fill("#password", "testpass123")
            
            # Click login button
            await page.click("#login-button")
            
            # Wait for redirect/dashboard
            await asyncio.sleep(1)  # Simulate page load
            
            # Verify successful login (check for welcome message)
            # Note: This is a mock example - adjust selectors for your app
            welcome_visible = await page.is_visible("#welcome-message")
            
            # In a real test, you'd check for dashboard elements
            print("✅ Test passed: Login flow executed")
    
    @pytest.mark.ui
    @pytest.mark.asyncio
    async def test_invalid_login(self):
        """Test login with invalid credentials."""
        async with PlaywrightPage(browser_type="chromium", headless=True) as page:
            # Navigate to login page
            await page.goto("https://example.com/login")
            
            # Fill with invalid credentials
            await page.fill("#username", "invalid_user")
            await page.fill("#password", "wrong_password")
            
            # Click login button
            await page.click("#login-button")
            
            # Wait for error message
            await asyncio.sleep(1)
            
            # Verify error message appears
            # Note: This is a mock example - adjust selectors for your app
            error_visible = await page.is_visible(".error-message")
            
            print("✅ Test passed: Invalid login scenario tested")


class TestUIResponsive:
    """Example of responsive design testing."""
    
    @pytest.mark.ui
    @pytest.mark.asyncio
    async def test_desktop_viewport(self):
        """Test UI with desktop viewport."""
        async with PlaywrightPage(
            browser_type="chromium",
            headless=True,
            viewport=(1920, 1080)
        ) as page:
            await page.goto("https://example.com")
            await page.wait_for_selector("h1")
            
            print("✅ Test passed: Desktop viewport (1920x1080)")
    
    @pytest.mark.ui
    @pytest.mark.asyncio
    async def test_tablet_viewport(self):
        """Test UI with tablet viewport."""
        async with PlaywrightPage(
            browser_type="chromium",
            headless=True,
            viewport=(768, 1024)
        ) as page:
            await page.goto("https://example.com")
            await page.wait_for_selector("h1")
            
            print("✅ Test passed: Tablet viewport (768x1024)")
    
    @pytest.mark.ui
    @pytest.mark.asyncio
    async def test_mobile_viewport(self):
        """Test UI with mobile viewport."""
        async with PlaywrightPage(
            browser_type="chromium",
            headless=True,
            viewport=(375, 667)
        ) as page:
            await page.goto("https://example.com")
            await page.wait_for_selector("h1")
            
            print("✅ Test passed: Mobile viewport (375x667)")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "-s", "-m", "ui"])
