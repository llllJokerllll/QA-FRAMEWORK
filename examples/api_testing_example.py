"""Test examples demonstrating framework usage"""

import pytest
import asyncio
from src.adapters.http.httpx_client import HTTPXClient
from src.core.entities.test_result import TestResult


class TestAPIExample:
    """Example API tests using the framework"""
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_users_from_jsonplaceholder(self):
        """Test GET request to JSONPlaceholder API"""
        client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
        
        try:
            response = await client.get("/users")
            
            # Assertions
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            assert len(data) > 0, "Response should not be empty"
            
            # Verify user structure
            user = data[0]
            assert "id" in user, "User should have 'id' field"
            assert "name" in user, "User should have 'name' field"
            assert "email" in user, "User should have 'email' field"
            
            print(f"✅ Test passed: Retrieved {len(data)} users")
            
        finally:
            await client.close()
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_user(self):
        """Test POST request to create user"""
        client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
        
        try:
            user_data = {
                "name": "Test User",
                "username": "testuser",
                "email": "test@example.com"
            }
            
            response = await client.post("/users", data=user_data)
            
            # Assertions
            assert response.status_code == 201, f"Expected 201, got {response.status_code}"
            
            data = response.json()
            assert data["name"] == "Test User", "User name should match"
            assert data["email"] == "test@example.com", "User email should match"
            assert "id" in data, "Response should include generated ID"
            
            print(f"✅ Test passed: Created user with ID {data['id']}")
            
        finally:
            await client.close()
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_single_post(self):
        """Test GET single resource"""
        client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
        
        try:
            response = await client.get("/posts/1")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            post = response.json()
            assert post["id"] == 1, "Post ID should be 1"
            assert "title" in post, "Post should have title"
            assert "body" in post, "Post should have body"
            
            print(f"✅ Test passed: Retrieved post '{post['title']}'")
            
        finally:
            await client.close()
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_api_timeout_handling(self):
        """Test that timeout configuration works"""
        client = HTTPXClient(
            base_url="https://jsonplaceholder.typicode.com",
            timeout=10  # 10 second timeout
        )
        
        try:
            response = await client.get("/users?_delay=5")
            assert response.status_code == 200
            
            print("✅ Test passed: Timeout handling works correctly")
            
        finally:
            await client.close()


class TestBasicAssertions:
    """Example basic assertions"""
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_status_code_assertions(self):
        """Test various status codes"""
        client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
        
        try:
            # Test 200 OK
            response = await client.get("/users")
            assert response.status_code == 200
            
            # Test 404 Not Found
            response = await client.get("/invalid-endpoint")
            assert response.status_code == 404
            
            print("✅ Test passed: Status code assertions work")
            
        finally:
            await client.close()
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_json_path_assertions(self):
        """Test JSON path-like assertions"""
        client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
        
        try:
            response = await client.get("/users")
            users = response.json()
            
            # Assert on array length
            assert len(users) == 10, f"Expected 10 users, got {len(users)}"
            
            # Assert on specific element property
            assert users[0]["name"] == "Leanne Graham"
            assert users[0]["email"] == "Sincere@april.biz"
            
            print("✅ Test passed: JSON path assertions work")
            
        finally:
            await client.close()


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "-s"])
