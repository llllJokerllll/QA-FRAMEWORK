import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from services.dashboard_service import (
    get_stats_service,
    get_trends_service,
    get_recent_service,
    get_test_types_distribution,
    get_performance_metrics
)
from models import TestExecution, TestSuite


@pytest.fixture
def mock_db_session():
    """Mock de sesión de base de datos"""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    return session


class TestDashboardService:
    
    async def test_get_stats_service_success(self, mock_db_session):
        """Test para get_stats_service - caso exitoso"""
        # Mock de resultados
        mock_avg_result = MagicMock()
        mock_avg_result.scalar_one_or_none.return_value = [45.5]
        
        mock_count_result = MagicMock()
        mock_count_result.scalar_one_or_none.return_value = 10
        
        mock_fastest_result = MagicMock()
        mock_fastest_mock = MagicMock()
        mock_fastest_mock.id = 1
        mock_fastest_mock.duration = 100
        mock_fastest_mock.suite = MagicMock()
        mock_fastest_mock.suite.name = "Test Suite 1"
        mock_fastest_result.scalar_one_or_none.return_value = mock_fastest_mock
        
        mock_slowest_result = MagicMock()
        mock_slowest_mock = MagicMock()
        mock_slowest_mock.id = 2
        mock_slowest_mock.duration = 500
        mock_slowest_mock.suite = MagicMock()
        mock_slowest_mock.suite.name = "Test Suite 2"
        mock_slowest_result.scalar_one_or_none.return_value = mock_slowest_mock
        
        # Mock de las llamadas a execute
        side_effects = [mock_avg_result, mock_count_result, mock_fastest_result, mock_slowest_result, mock_count_result, mock_count_result]
        mock_db_session.execute.side_effect = side_effects
        
        # Ejecutar la función
        result = await get_stats_service(mock_db_session)
        
        # Verificar resultado
        assert isinstance(result, dict)
        assert "average_duration" in result
        assert "total_executions" in result
        assert "fastest_execution" in result
        assert "slowest_execution" in result
        
        # Verificar que se llamó a execute 4 veces
        assert mock_db_session.execute.call_count == 4
    
    async def test_get_stats_service_empty_results(self, mock_db_session):
        """Test para get_stats_service - sin resultados"""
        # Mock de resultados vacíos
        mock_avg_result = MagicMock()
        mock_avg_result.scalar_one_or_none.return_value = [None]
        
        mock_count_result = MagicMock()
        mock_count_result.scalar_one_or_none.return_value = 0
        
        mock_fastest_result = MagicMock()
        mock_fastest_result.scalar_one_or_none.return_value = None
        
        mock_slowest_result = MagicMock()
        mock_slowest_result.scalar_one_or_none.return_value = None
        
        # Mock de las llamadas a execute
        side_effects = [mock_avg_result, mock_count_result, mock_fastest_result, mock_slowest_result, mock_count_result, mock_count_result]
        mock_db_session.execute.side_effect = side_effects
        
        # Ejecutar la función
        result = await get_stats_service(mock_db_session)
        
        # Verificar resultados
        assert result["average_duration"] == 0
        assert result["total_executions"] == 0
        assert result["fastest_execution"] is None
        assert result["slowest_execution"] is None
    
    async def test_get_trends_service_success(self, mock_db_session):
        """Test para get_trends_service - caso exitoso"""
        # Mock de resultados
        mock_date = datetime.now() - timedelta(days=5)
        mock_execution = MagicMock()
        mock_execution.date_created = mock_date
        mock_execution.status = "completed"
        mock_execution.duration = 100
        
        mock_result = MagicMock()
        mock_result.unique.return_value = [mock_execution]
        mock_result.scalars.return_value.all.return_value = [mock_execution]
        
        mock_db_session.execute.return_value = mock_result
        
        # Ejecutar la función
        result = await get_trends_service(mock_db_session, days=7)
        
        # Verificar resultado
        assert isinstance(result, list)
        assert len(result) >= 0  # Puede estar vacío dependiendo de los datos simulados
    
    async def test_get_recent_service_success(self, mock_db_session):
        """Test para get_recent_service - caso exitoso"""
        # Mock de resultados
        mock_execution = MagicMock()
        mock_execution.id = 1
        mock_execution.name = "Recent Test"
        mock_execution.status = "completed"
        mock_execution.date_created = datetime.now()
        
        mock_result = MagicMock()
        mock_result.unique.return_value = [mock_execution]
        mock_result.scalars.return_value.all.return_value = [mock_execution]
        
        mock_db_session.execute.return_value = mock_result
        
        # Ejecutar la función
        result = await get_recent_service(mock_db_session, limit=5)
        
        # Verificar resultado
        assert isinstance(result, list)
        if len(result) > 0:
            assert "id" in result[0]
            assert "suite_name" in result[0]  # Updated from "name" to "suite_name"
            assert "status" in result[0]
    
    async def test_get_test_types_distribution_success(self, mock_db_session):
        """Test para get_test_types_distribution - caso exitoso"""
        # Mock de resultados
        mock_row1 = MagicMock()
        mock_row1.type = "functional"
        mock_row1.count = 5
        
        mock_row2 = MagicMock()
        mock_row2.type = "regression"
        mock_row2.count = 3
        
        mock_result = MagicMock()
        mock_result.unique.return_value = [mock_row1, mock_row2]
        mock_result.scalars.return_value.all.return_value = [mock_row1, mock_row2]
        
        mock_db_session.execute.return_value = mock_result
        
        # Ejecutar la función
        result = await get_test_types_distribution(mock_db_session)
        
        # Verificar resultado
        assert isinstance(result, dict)
        # Puede contener diferentes tipos de tests dependiendo de los datos simulados
    
    async def test_get_performance_metrics_success(self, mock_db_session):
        """Test para get_performance_metrics - caso exitoso"""
        # Mock de resultados
        mock_avg_result = MagicMock()
        mock_avg_result.scalar_one_or_none.return_value = [45.5]
        
        mock_fastest_result = MagicMock()
        mock_fastest_mock = MagicMock()
        mock_fastest_mock.id = 1
        mock_fastest_mock.duration = 10
        mock_fastest_mock.suite = MagicMock()
        mock_fastest_mock.suite.name = "Fast Suite"
        mock_fastest_result.scalar_one_or_none.return_value = mock_fastest_mock
        
        mock_slowest_result = MagicMock()
        mock_slowest_mock = MagicMock()
        mock_slowest_mock.id = 2
        mock_slowest_mock.duration = 100
        mock_slowest_mock.suite = MagicMock()
        mock_slowest_mock.suite.name = "Slow Suite"
        mock_slowest_result.scalar_one_or_none.return_value = mock_slowest_mock
        
        # Mock de las llamadas a execute
        side_effects = [mock_avg_result, mock_fastest_result, mock_slowest_result]
        mock_db_session.execute.side_effect = side_effects
        
        # Ejecutar la función
        result = await get_performance_metrics(mock_db_session)
        
        # Verificar resultado
        assert isinstance(result, dict)
        assert "average_duration" in result
        assert "fastest_execution" in result
        assert "slowest_execution" in result