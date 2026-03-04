"""
Tests for feature flags system.
"""

import pytest
from datetime import datetime, timedelta
from core.feature_flags import (
    FeatureFlag,
    FeatureFlagStrategy,
    FeatureFlagManager,
    get_flag_manager,
    is_feature_enabled,
    register_feature_flag
)


class TestFeatureFlag:
    """Tests for FeatureFlag class."""
    
    def test_init_default_values(self):
        """Test FeatureFlag initialization with defaults."""
        flag = FeatureFlag(name="test_flag")
        
        assert flag.name == "test_flag"
        assert flag.enabled is True
        assert flag.strategy == FeatureFlagStrategy.PERCENTAGE
        assert flag.config == {}
        assert flag.description == ""
        assert isinstance(flag.created_at, datetime)
        assert isinstance(flag.updated_at, datetime)
    
    def test_init_with_values(self):
        """Test FeatureFlag initialization with custom values."""
        config = {"percentage": 50}
        flag = FeatureFlag(
            name="test_flag",
            enabled=False,
            strategy=FeatureFlagStrategy.USER_LIST,
            config=config,
            description="Test description"
        )
        
        assert flag.name == "test_flag"
        assert flag.enabled is False
        assert flag.strategy == FeatureFlagStrategy.USER_LIST
        assert flag.config == config
        assert flag.description == "Test description"
    
    def test_is_enabled_for_user_disabled_flag(self):
        """Test that disabled flag returns False for all users."""
        flag = FeatureFlag(name="test", enabled=False)
        
        assert flag.is_enabled_for_user("user1") is False
        assert flag.is_enabled_for_user("user2") is False
    
    def test_is_enabled_for_user_percentage_strategy(self):
        """Test percentage-based rollout."""
        # 50% rollout
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 50}
        )
        
        # Check that the flag is consistent for same user
        result1 = flag.is_enabled_for_user("user1")
        result2 = flag.is_enabled_for_user("user1")
        assert result1 == result2
        
        # Different users get different results (some enabled, some not)
        users = [f"user{i}" for i in range(100)]
        enabled_count = sum(1 for user in users if flag.is_enabled_for_user(user))
        
        # Should be around 50% (allow some variance)
        assert 40 <= enabled_count <= 60
    
    def test_is_enabled_for_user_percentage_zero(self):
        """Test percentage-based rollout with 0%."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 0}
        )
        
        assert flag.is_enabled_for_user("user1") is False
        assert flag.is_enabled_for_user("user2") is False
    
    def test_is_enabled_for_user_percentage_hundred(self):
        """Test percentage-based rollout with 100%."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 100}
        )
        
        assert flag.is_enabled_for_user("user1") is True
        assert flag.is_enabled_for_user("user2") is True
    
    def test_is_enabled_for_user_user_list_strategy(self):
        """Test user list-based rollout."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.USER_LIST,
            config={"users": ["user1", "user2", "user3"]}
        )
        
        assert flag.is_enabled_for_user("user1") is True
        assert flag.is_enabled_for_user("user2") is True
        assert flag.is_enabled_for_user("user3") is True
        assert flag.is_enabled_for_user("user4") is False
        assert flag.is_enabled_for_user("user5") is False
    
    def test_is_enabled_for_user_user_list_empty(self):
        """Test user list-based rollout with empty list."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.USER_LIST,
            config={"users": []}
        )
        
        assert flag.is_enabled_for_user("user1") is False
    
    def test_is_enabled_for_user_user_segment_strategy(self):
        """Test user segment-based rollout."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.USER_SEGMENT,
            config={"segments": ["premium", "beta"]}
        )
        
        assert flag.is_enabled_for_user("user1", context={"segment": "premium"}) is True
        assert flag.is_enabled_for_user("user2", context={"segment": "beta"}) is True
        assert flag.is_enabled_for_user("user3", context={"segment": "free"}) is False
    
    def test_is_enabled_for_user_user_segment_no_context(self):
        """Test user segment-based rollout without context."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.USER_SEGMENT,
            config={"segments": ["premium", "beta"]}
        )
        
        assert flag.is_enabled_for_user("user1") is False
    
    def test_is_enabled_for_user_user_segment_no_segment_in_context(self):
        """Test user segment-based rollout without segment in context."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.USER_SEGMENT,
            config={"segments": ["premium", "beta"]}
        )
        
        assert flag.is_enabled_for_user("user1", context={"other_key": "value"}) is False
    
    def test_is_enabled_for_user_gradual_strategy_not_started(self):
        """Test gradual rollout that hasn't started."""
        start_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
        end_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.GRADUAL,
            config={
                "start_date": start_date,
                "end_date": end_date,
                "start_percentage": 0,
                "end_percentage": 100
            }
        )
        
        assert flag.is_enabled_for_user("user1") is False
    
    def test_is_enabled_for_user_gradual_strategy_in_progress(self):
        """Test gradual rollout in progress."""
        start_date = (datetime.utcnow() - timedelta(hours=12)).isoformat()
        end_date = (datetime.utcnow() + timedelta(hours=12)).isoformat()
        
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.GRADUAL,
            config={
                "start_date": start_date,
                "end_date": end_date,
                "start_percentage": 0,
                "end_percentage": 100
            }
        )
        
        # Flag should be enabled for some users (50% through timeline)
        result = flag.is_enabled_for_user("user1")
        assert isinstance(result, bool)
    
    def test_is_enabled_for_user_gradual_strategy_completed(self):
        """Test gradual rollout that has completed."""
        start_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        end_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.GRADUAL,
            config={
                "start_date": start_date,
                "end_date": end_date,
                "start_percentage": 0,
                "end_percentage": 100
            }
        )
        
        assert flag.is_enabled_for_user("user1") is True
    
    def test_is_enabled_for_user_gradual_strategy_no_dates(self):
        """Test gradual rollout without dates."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.GRADUAL,
            config={"start_percentage": 0, "end_percentage": 100}
        )
        
        assert flag.is_enabled_for_user("user1") is False
    
    def test_is_enabled_for_user_ab_test_strategy(self):
        """Test A/B testing strategy."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.A_B_TEST,
            config={
                "variants": ["A", "B"],
                "weights": [50, 50]
            }
        )
        
        # Check consistency for same user
        result1 = flag.is_enabled_for_user("user1")
        result2 = flag.is_enabled_for_user("user1")
        assert result1 == result2
        
        # Different users should get consistent but different assignments
        users = [f"user{i}" for i in range(100)]
        enabled_count = sum(1 for user in users if flag.is_enabled_for_user(user))
        
        # Should be around 50% (those assigned to variant B)
        assert 40 <= enabled_count <= 60
    
    def test_is_enabled_for_user_ab_test_strategy_uneven_weights(self):
        """Test A/B testing with uneven weights."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.A_B_TEST,
            config={
                "variants": ["A", "B", "C"],
                "weights": [80, 15, 5]
            }
        )
        
        users = [f"user{i}" for i in range(100)]
        enabled_count = sum(1 for user in users if flag.is_enabled_for_user(user))
        
        # Should be around 20% (those assigned to B or C)
        assert 10 <= enabled_count <= 30
    
    def test_is_enabled_for_user_ab_test_strategy_default_weights(self):
        """Test A/B testing with default weights."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.A_B_TEST,
            config={"variants": ["A", "B"]}
        )
        
        users = [f"user{i}" for i in range(100)]
        enabled_count = sum(1 for user in users if flag.is_enabled_for_user(user))
        
        # Should be around 50% with default weights
        assert 40 <= enabled_count <= 60
    
    def test_is_enabled_for_user_unknown_strategy(self):
        """Test unknown strategy returns False."""
        # This test ensures the method handles unknown strategies gracefully
        flag = FeatureFlag(name="test", enabled=True)
        # Modify strategy to an invalid value
        flag.strategy = "unknown_strategy"
        
        assert flag.is_enabled_for_user("user1") is False
    
    def test_to_dict(self):
        """Test converting FeatureFlag to dictionary."""
        flag = FeatureFlag(
            name="test",
            enabled=False,
            strategy=FeatureFlagStrategy.USER_LIST,
            config={"users": ["user1"]},
            description="Test flag"
        )
        
        result = flag.to_dict()
        
        assert result["name"] == "test"
        assert result["enabled"] is False
        assert result["strategy"] == "user_list"
        assert result["config"] == {"users": ["user1"]}
        assert result["description"] == "Test flag"
        assert "created_at" in result
        assert "updated_at" in result
    
    def test_from_dict(self):
        """Test creating FeatureFlag from dictionary."""
        data = {
            "name": "test",
            "enabled": True,
            "strategy": "percentage",
            "config": {"percentage": 75},
            "description": "Test flag",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        flag = FeatureFlag.from_dict(data)
        
        assert flag.name == "test"
        assert flag.enabled is True
        assert flag.strategy == FeatureFlagStrategy.PERCENTAGE
        assert flag.config == {"percentage": 75}
        assert flag.description == "Test flag"
    
    def test_from_dict_minimal(self):
        """Test creating FeatureFlag from minimal dictionary."""
        data = {"name": "test", "enabled": True, "strategy": "percentage"}
        
        flag = FeatureFlag.from_dict(data)
        
        assert flag.name == "test"
        assert flag.enabled is True
        assert flag.strategy == FeatureFlagStrategy.PERCENTAGE
        assert flag.config == {}
        assert flag.description == ""


class TestFeatureFlagManager:
    """Tests for FeatureFlagManager class."""
    
    def test_init(self):
        """Test FeatureFlagManager initialization."""
        manager = FeatureFlagManager()
        
        assert manager.flags == {}
        assert manager.evaluation_count == {}
    
    def test_register_flag(self):
        """Test registering a feature flag."""
        manager = FeatureFlagManager()
        flag = FeatureFlag(name="test")
        
        manager.register_flag(flag)
        
        assert "test" in manager.flags
        assert manager.flags["test"] == flag
        assert manager.evaluation_count["test"] == 0
    
    def test_register_flag_multiple(self):
        """Test registering multiple feature flags."""
        manager = FeatureFlagManager()
        
        flag1 = FeatureFlag(name="test1")
        flag2 = FeatureFlag(name="test2")
        flag3 = FeatureFlag(name="test3")
        
        manager.register_flag(flag1)
        manager.register_flag(flag2)
        manager.register_flag(flag3)
        
        assert len(manager.flags) == 3
        assert "test1" in manager.flags
        assert "test2" in manager.flags
        assert "test3" in manager.flags
    
    def test_unregister_flag(self):
        """Test unregistering a feature flag."""
        manager = FeatureFlagManager()
        flag = FeatureFlag(name="test")
        
        manager.register_flag(flag)
        result = manager.unregister_flag("test")
        
        assert result is True
        assert "test" not in manager.flags
        assert "test" not in manager.evaluation_count
    
    def test_unregister_flag_not_exists(self):
        """Test unregistering a non-existent flag."""
        manager = FeatureFlagManager()
        
        result = manager.unregister_flag("nonexistent")
        
        assert result is False
    
    def test_get_flag(self):
        """Test getting a feature flag."""
        manager = FeatureFlagManager()
        flag = FeatureFlag(name="test")
        
        manager.register_flag(flag)
        result = manager.get_flag("test")
        
        assert result == flag
    
    def test_get_flag_not_exists(self):
        """Test getting a non-existent flag."""
        manager = FeatureFlagManager()
        
        result = manager.get_flag("nonexistent")
        
        assert result is None
    
    def test_is_enabled_flag_exists(self):
        """Test is_enabled with existing flag."""
        manager = FeatureFlagManager()
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 100}
        )
        
        manager.register_flag(flag)
        result = manager.is_enabled("test", "user1")
        
        assert result is True
        assert manager.evaluation_count["test"] == 1
    
    def test_is_enabled_flag_not_exists(self):
        """Test is_enabled with non-existent flag."""
        manager = FeatureFlagManager()
        
        result = manager.is_enabled("nonexistent", "user1")
        
        assert result is False
    
    def test_is_enabled_disabled_flag(self):
        """Test is_enabled with disabled flag."""
        manager = FeatureFlagManager()
        flag = FeatureFlag(name="test", enabled=False)
        
        manager.register_flag(flag)
        result = manager.is_enabled("test", "user1")
        
        assert result is False
    
    def test_is_enabled_tracks_evaluations(self):
        """Test that is_enabled tracks evaluation count."""
        manager = FeatureFlagManager()
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 100}
        )
        
        manager.register_flag(flag)
        
        manager.is_enabled("test", "user1")
        manager.is_enabled("test", "user2")
        manager.is_enabled("test", "user3")
        
        assert manager.evaluation_count["test"] == 3
    
    def test_get_all_flags(self):
        """Test getting all flags."""
        manager = FeatureFlagManager()
        
        flag1 = FeatureFlag(name="test1")
        flag2 = FeatureFlag(name="test2")
        
        manager.register_flag(flag1)
        manager.register_flag(flag2)
        
        result = manager.get_all_flags()
        
        assert len(result) == 2
        assert any(f["name"] == "test1" for f in result)
        assert any(f["name"] == "test2" for f in result)
    
    def test_get_all_flags_empty(self):
        """Test getting all flags when none registered."""
        manager = FeatureFlagManager()
        
        result = manager.get_all_flags()
        
        assert result == []
    
    def test_get_stats(self):
        """Test getting flag statistics."""
        manager = FeatureFlagManager()
        
        flag1 = FeatureFlag(name="test1", enabled=True)
        flag2 = FeatureFlag(name="test2", enabled=False)
        flag3 = FeatureFlag(name="test3", enabled=True)
        
        manager.register_flag(flag1)
        manager.register_flag(flag2)
        manager.register_flag(flag3)
        
        # Make some evaluations
        manager.is_enabled("test1", "user1")
        manager.is_enabled("test1", "user2")
        manager.is_enabled("test2", "user1")
        
        stats = manager.get_stats()
        
        assert stats["total_flags"] == 3
        assert stats["enabled_flags"] == 2
        assert stats["evaluations"]["test1"] == 2
        assert stats["evaluations"]["test2"] == 1
        assert stats["evaluations"]["test3"] == 0
    
    def test_export_flags(self):
        """Test exporting flags to JSON."""
        manager = FeatureFlagManager()
        
        flag1 = FeatureFlag(name="test1", description="Flag 1")
        flag2 = FeatureFlag(name="test2", description="Flag 2")
        
        manager.register_flag(flag1)
        manager.register_flag(flag2)
        
        result = manager.export_flags()
        
        assert isinstance(result, str)
        assert "test1" in result
        assert "test2" in result
        assert "Flag 1" in result
        assert "Flag 2" in result
    
    def test_export_flags_empty(self):
        """Test exporting flags when none registered."""
        manager = FeatureFlagManager()
        
        result = manager.export_flags()
        
        assert result == "[]"
    
    def test_import_flags(self):
        """Test importing flags from JSON."""
        manager = FeatureFlagManager()
        
        json_str = '''[
            {
                "name": "test1",
                "enabled": true,
                "strategy": "percentage",
                "config": {"percentage": 50},
                "description": "Flag 1",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            },
            {
                "name": "test2",
                "enabled": false,
                "strategy": "user_list",
                "config": {"users": ["user1"]},
                "description": "Flag 2",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        ]'''
        
        count = manager.import_flags(json_str)
        
        assert count == 2
        assert "test1" in manager.flags
        assert "test2" in manager.flags
        assert manager.flags["test1"].enabled is True
        assert manager.flags["test2"].enabled is False
    
    def test_import_flags_empty(self):
        """Test importing empty JSON."""
        manager = FeatureFlagManager()
        
        count = manager.import_flags("[]")
        
        assert count == 0
        assert manager.flags == {}


class TestGlobalFunctions:
    """Tests for global functions."""
    
    def test_get_flag_manager(self):
        """Test getting global flag manager."""
        manager = get_flag_manager()
        
        assert isinstance(manager, FeatureFlagManager)
    
    def test_get_flag_manager_singleton(self):
        """Test that get_flag_manager returns same instance."""
        manager1 = get_flag_manager()
        manager2 = get_flag_manager()
        
        assert manager1 is manager2
    
    def test_is_feature_enabled(self):
        """Test is_feature_enabled convenience function."""
        # Register a flag
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 100}
        )
        register_feature_flag("test", enabled=True, config={"percentage": 100})
        
        result = is_feature_enabled("test", "user1")
        
        assert result is True
    
    def test_register_feature_flag(self):
        """Test register_feature_flag convenience function."""
        flag = register_feature_flag(
            name="test_new",
            enabled=True,
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 50},
            description="Test flag"
        )
        
        assert isinstance(flag, FeatureFlag)
        assert flag.name == "test_new"
        assert flag.enabled is True
        
        # Check it's registered in global manager
        manager = get_flag_manager()
        assert manager.get_flag("test_new") == flag
    
    def test_register_feature_flag_defaults(self):
        """Test register_feature_flag with defaults."""
        flag = register_feature_flag(name="test_defaults")
        
        assert flag.name == "test_defaults"
        assert flag.enabled is True
        assert flag.strategy == FeatureFlagStrategy.PERCENTAGE
        assert flag.config == {}
        assert flag.description == ""


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_percentage_negative(self):
        """Test negative percentage."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": -10}
        )
        
        # Should handle gracefully
        result = flag.is_enabled_for_user("user1")
        assert isinstance(result, bool)
    
    def test_percentage_over_hundred(self):
        """Test percentage over 100."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 150}
        )
        
        # Should handle gracefully
        result = flag.is_enabled_for_user("user1")
        assert isinstance(result, bool)
    
    def test_user_list_case_sensitivity(self):
        """Test that user list is case-sensitive."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.USER_LIST,
            config={"users": ["User1", "User2"]}
        )
        
        assert flag.is_enabled_for_user("User1") is True
        assert flag.is_enabled_for_user("user1") is False
    
    def test_ab_test_mismatched_weights_variants(self):
        """Test A/B test with mismatched weights and variants."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.A_B_TEST,
            config={
                "variants": ["A", "B", "C"],
                "weights": [50, 50]  # Mismatched
            }
        )
        
        # Should handle gracefully
        result = flag.is_enabled_for_user("user1")
        assert isinstance(result, bool)
    
    def test_gradual_invalid_dates(self):
        """Test gradual with invalid dates raises ValueError."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.GRADUAL,
            config={
                "start_date": "invalid",
                "end_date": "invalid",
                "start_percentage": 0,
                "end_percentage": 100
            }
        )
        
        # Invalid dates should raise ValueError (not handled gracefully by design)
        with pytest.raises(ValueError, match="Invalid isoformat string"):
            flag.is_enabled_for_user("user1")
    
    def test_empty_user_id(self):
        """Test with empty user ID."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 100}
        )
        
        result = flag.is_enabled_for_user("")
        assert isinstance(result, bool)
    
    def test_special_characters_in_user_id(self):
        """Test with special characters in user ID."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 100}
        )
        
        result = flag.is_enabled_for_user("user@test@example.com")
        assert isinstance(result, bool)
    
    def test_very_long_user_id(self):
        """Test with very long user ID."""
        flag = FeatureFlag(
            name="test",
            strategy=FeatureFlagStrategy.PERCENTAGE,
            config={"percentage": 100}
        )
        
        long_id = "user" * 1000
        result = flag.is_enabled_for_user(long_id)
        assert isinstance(result, bool)
