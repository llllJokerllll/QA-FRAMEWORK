"""
Unit tests for api_key_service.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestApiKeyServiceGenerate:
    """Tests for ApiKeyService static methods."""

    def test_generate_api_key_format(self):
        from services.api_key_service import ApiKeyService

        key = ApiKeyService.generate_api_key()

        assert key.startswith("qaf_live_")
        assert len(key) > 20

    def test_generate_api_key_unique(self):
        from services.api_key_service import ApiKeyService

        key1 = ApiKeyService.generate_api_key()
        key2 = ApiKeyService.generate_api_key()

        assert key1 != key2

    def test_hash_api_key_deterministic(self):
        from services.api_key_service import ApiKeyService

        key = "qaf_live_testkey123"
        hash1 = ApiKeyService.hash_api_key(key)
        hash2 = ApiKeyService.hash_api_key(key)

        assert hash1 == hash2

    def test_hash_api_key_different_inputs(self):
        from services.api_key_service import ApiKeyService

        hash1 = ApiKeyService.hash_api_key("key_one")
        hash2 = ApiKeyService.hash_api_key("key_two")

        assert hash1 != hash2

    def test_hash_api_key_sha256_length(self):
        from services.api_key_service import ApiKeyService

        hashed = ApiKeyService.hash_api_key("test")
        assert len(hashed) == 64  # SHA256 hex = 64 chars


class TestApiKeyServiceCreate:
    """Tests for ApiKeyService.create_api_key."""

    @pytest.mark.asyncio
    async def test_create_api_key_success(self):
        from services.api_key_service import ApiKeyService

        mock_db = AsyncMock()
        mock_api_key_record = MagicMock()
        mock_api_key_record.id = "key-uuid-123"
        mock_api_key_record.name = "My Key"
        mock_api_key_record.scopes = ["read"]
        mock_api_key_record.created_at = datetime.utcnow()
        mock_api_key_record.expires_at = None
        mock_db.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, 'id', 'key-uuid-123') or None)

        key_request = MagicMock()
        key_request.name = "My Key"
        key_request.scopes = ["read"]
        key_request.expires_at = None

        with patch("services.api_key_service.ApiKey") as MockApiKey:
            mock_instance = MagicMock()
            mock_instance.id = "key-uuid-123"
            mock_instance.name = "My Key"
            mock_instance.scopes = ["read"]
            mock_instance.created_at = datetime.utcnow()
            mock_instance.expires_at = None
            MockApiKey.return_value = mock_instance

            result = await ApiKeyService.create_api_key(mock_db, "user-1", key_request)

        assert result.key.startswith("qaf_live_")
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_api_key_with_expiry(self):
        from services.api_key_service import ApiKeyService

        mock_db = AsyncMock()
        expires = datetime.utcnow() + timedelta(days=30)

        key_request = MagicMock()
        key_request.name = "Expiring Key"
        key_request.scopes = ["read", "write"]
        key_request.expires_at = expires

        with patch("services.api_key_service.ApiKey") as MockApiKey:
            mock_instance = MagicMock()
            mock_instance.id = "key-2"
            mock_instance.name = "Expiring Key"
            mock_instance.scopes = ["read", "write"]
            mock_instance.created_at = datetime.utcnow()
            mock_instance.expires_at = expires
            MockApiKey.return_value = mock_instance

            result = await ApiKeyService.create_api_key(mock_db, "user-2", key_request)

        assert result.expires_at == expires


class TestApiKeyServiceValidate:
    """Tests for ApiKeyService.validate_api_key."""

    @pytest.mark.asyncio
    async def test_validate_valid_key(self):
        from services.api_key_service import ApiKeyService

        mock_db = AsyncMock()
        mock_key_record = MagicMock()
        mock_key_record.expires_at = None
        mock_key_record.user_id = "user-1"
        mock_key_record.last_used_at = None

        mock_user = MagicMock()

        mock_key_result = MagicMock()
        mock_key_result.scalar_one_or_none.return_value = mock_key_record

        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_user

        mock_db.execute.side_effect = [mock_key_result, mock_user_result]

        result = await ApiKeyService.validate_api_key(mock_db, "qaf_live_validkey123")

        assert result == mock_user
        mock_db.commit.assert_called_once()  # last_used_at updated

    @pytest.mark.asyncio
    async def test_validate_invalid_prefix(self):
        from services.api_key_service import ApiKeyService

        mock_db = AsyncMock()
        result = await ApiKeyService.validate_api_key(mock_db, "invalid_key_format")

        assert result is None
        mock_db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_validate_empty_key(self):
        from services.api_key_service import ApiKeyService

        mock_db = AsyncMock()
        result = await ApiKeyService.validate_api_key(mock_db, "")

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_none_key(self):
        from services.api_key_service import ApiKeyService

        mock_db = AsyncMock()
        result = await ApiKeyService.validate_api_key(mock_db, None)

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_key_not_found(self):
        from services.api_key_service import ApiKeyService

        mock_db = AsyncMock()

        mock_key_result = MagicMock()
        mock_key_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_key_result

        result = await ApiKeyService.validate_api_key(mock_db, "qaf_live_unknownkey")

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_expired_key(self):
        from services.api_key_service import ApiKeyService

        mock_db = AsyncMock()
        mock_key_record = MagicMock()
        mock_key_record.expires_at = datetime.utcnow() - timedelta(days=1)  # expired

        mock_key_result = MagicMock()
        mock_key_result.scalar_one_or_none.return_value = mock_key_record
        mock_db.execute.return_value = mock_key_result

        result = await ApiKeyService.validate_api_key(mock_db, "qaf_live_expiredkey")

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_key_not_expired(self):
        from services.api_key_service import ApiKeyService

        mock_db = AsyncMock()
        mock_key_record = MagicMock()
        mock_key_record.expires_at = datetime.utcnow() + timedelta(days=30)  # future
        mock_key_record.user_id = "user-1"

        mock_user = MagicMock()

        mock_key_result = MagicMock()
        mock_key_result.scalar_one_or_none.return_value = mock_key_record

        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_user

        mock_db.execute.side_effect = [mock_key_result, mock_user_result]

        result = await ApiKeyService.validate_api_key(mock_db, "qaf_live_validfuturekey")

        assert result == mock_user
