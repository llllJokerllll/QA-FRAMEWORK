"""
Test Search Schemas

Simple test to verify search schema validation.
"""

from pydantic import ValidationError
from schemas.search import SearchQuery, SearchResults, SearchResponse


def test_search_query_schema():
    """Test SearchQuery schema validation."""
    print("🔍 Testing Search Schemas")
    print("=" * 50)
    
    # Test valid queries
    test_cases = [
        {
            "name": "Basic search",
            "data": {"q": "login"},
            "expected": {"q": "login", "types": None, "limit": 10, "offset": 0}
        },
        {
            "name": "Search with types filter",
            "data": {"q": "auth", "types": ["suites", "cases"]},
            "expected": {"q": "auth", "types": ["suites", "cases"], "limit": 10, "offset": 0}
        },
        {
            "name": "Search with pagination",
            "data": {"q": "test", "limit": 20, "offset": 10},
            "expected": {"q": "test", "types": None, "limit": 20, "offset": 10}
        },
        {
            "name": "Search with all parameters",
            "data": {"q": "user", "types": ["users"], "limit": 5, "offset": 2},
            "expected": {"q": "user", "types": ["users"], "limit": 5, "offset": 2}
        }
    ]
    
    print("\n📋 Test Cases:")
    for i, test_case in enumerate(test_cases, 1):
        try:
            query = SearchQuery(**test_case["data"])
            expected = test_case["expected"]
            
            # Verify all fields match
            assert query.q == expected["q"], f"q mismatch: {query.q} != {expected['q']}"
            assert query.types == expected["types"], f"types mismatch: {query.types} != {expected['types']}"
            assert query.limit == expected["limit"], f"limit mismatch: {query.limit} != {expected['limit']}"
            assert query.offset == expected["offset"], f"offset mismatch: {query.offset} != {expected['offset']}"
            
            print(f"  ✅ {i}. {test_case['name']}")
        except ValidationError as e:
            print(f"  ❌ {i}. {test_case['name']} - Validation Error: {e}")
        except AssertionError as e:
            print(f"  ❌ {i}. {test_case['name']} - Assertion Error: {e}")
        except Exception as e:
            print(f"  ❌ {i}. {test_case['name']} - Error: {e}")
    
    # Test invalid queries
    print("\n🚫 Testing Invalid Queries (should fail):")
    invalid_cases = [
        {"name": "Empty query", "data": {"q": ""}},
        {"name": "Query too long", "data": {"q": "x" * 201}},
        {"name": "Limit too high", "data": {"q": "test", "limit": 100}},
        {"name": "Negative offset", "data": {"q": "test", "offset": -1}},
    ]
    
    for i, test_case in enumerate(invalid_cases, 1):
        try:
            query = SearchQuery(**test_case["data"])
            print(f"  ⚠️  {i}. {test_case['name']} - Should have failed but didn't!")
        except ValidationError:
            print(f"  ✅ {i}. {test_case['name']} - Correctly rejected")
        except Exception as e:
            print(f"  ❌ {i}. {test_case['name']} - Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Schema validation tests completed!")


if __name__ == "__main__":
    test_search_query_schema()
