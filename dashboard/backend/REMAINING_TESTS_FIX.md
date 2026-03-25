# Fix Remaining 47 Failing Tests

## Current Status
- **730 passing** (93.3%)
- **47 failing**
- **Coverage**: 27.91%

## Known Failing Categories

### Parallel Execution (11 tests)
File: `tests/services/test_parallel_execution_service.py`
Tests:
- test_release_resource
- test_distribute_round_robin
- test_distribute_load_aware
- test_execute_parallel_with_failures
- test_execute_single_test_with_error
- test_execute_parallel_with_skipped_tests
(and 5 more)

### Batch Execution (3 tests)
File: `tests/services/test_batch_execution_service.py`
Tests:
- test_execute_batch_with_complex_executor
- test_execute_batch_with_skipped_tests
- test_execute_batch_performance_optimization

### Auth (3 tests)
File: `tests/test_auth.py`
Tests:
- test_create_access_token
- test_create_access_token_with_expiry
- test_get_current_user_success

### Other (~30 tests)
Various files - need identification

## Context
- **Working Directory**: `/home/ubuntu/qa-framework/dashboard/backend`
- **Redis**: Use Railway Redis (configured in conftest.py)
- **NO MOCKS** for Redis - use real connection

## Your Task
1. Run `pytest tests/ -v --tb=short` to get full list of failures
2. Group failing tests by file/category
3. Fix tests systematically:
   - Read the test file
   - Understand what's being tested
   - Read the source code being tested
   - Fix the test OR the code (whichever is wrong)
4. Commit incrementally with descriptive messages
5. Run full suite to verify no regressions

## Recent Fixes (for reference)
- `391652e` - Fix skipped status tracking
- `7fd883c` - Fix timeout handling
- `e89dc6e` - Fix cache integration, error tracking

## Success Criteria
- All tests passing (or 95%+ pass rate)
- No regressions
- Coverage improved

## Commands to Start
```bash
cd /home/ubuntu/qa-framework/dashboard/backend
pytest tests/ -v --tb=short 2>&1 | grep -E "(FAILED|ERROR)" | head -60
```
