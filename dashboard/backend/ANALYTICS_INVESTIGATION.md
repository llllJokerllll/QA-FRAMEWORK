# Analytics Collection Error Investigation

## Problem
`test_analytics_service.py` passes 17/17 tests when run alone, but causes collection error when run with full test suite.

## Context
- **Working Directory**: `/home/ubuntu/qa-framework/dashboard/backend`
- **Test File**: `tests/test_analytics_service.py`
- **Redis URL**: Already configured in conftest.py
- **Current Status**: 17/17 passing when run isolated

## Your Task
1. Run `pytest tests/test_analytics_service.py -v` to confirm it passes alone
2. Run `pytest tests/ -v --collect-only` to see if there's a collection error
3. Investigate WHY it fails during collection with full suite
4. Look for:
   - Import conflicts
   - Fixture clashes
   - Module-level side effects
   - Circular dependencies
5. Fix the root cause
6. Commit with message: `fix(tests): resolve analytics service collection error`

## Success Criteria
- `pytest tests/` runs without collection errors
- All 17 analytics tests still pass
- No regressions in other tests

## Commands to Start
```bash
cd /home/ubuntu/qa-framework/dashboard/backend
pytest tests/test_analytics_service.py -v
pytest tests/ --collect-only 2>&1 | head -100
```
