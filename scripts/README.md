# Pre-Push Validation

## Overview
The `pre_push_check.py` script automatically validates your code before pushing to catch common errors like:
- Missing imports (`os`, `Path`, `numpy`, `PIL`)
- Syntax errors
- Import failures
- Test failures

## Usage

### Manual Check (Recommended)
Before pushing, always run:
```bash
python3 scripts/pre_push_check.py
```

### Automatic Check (Git Hook)
To install the git pre-push hook (runs automatically before every push):
```bash
chmod +x .git/hooks/pre-push
```

Then every `git push` will automatically run the checks. If checks fail, the push is blocked.

To skip checks (not recommended):
```bash
git push --no-verify
```

## What It Checks

1. **Syntax Validation** - Ensures all Python files have valid syntax
2. **Import Validation** - Checks for missing imports:
   - `os` module usage
   - `Path` from pathlib
   - `numpy` / `np`
   - `PIL` / `Image`
3. **Import Testing** - Actually imports all critical modules to verify they work
4. **Test Suite** - Runs full pytest suite
5. **Changed Files** - Ensures all changed Python files are validated

## Example Output

```
============================================================
COMPREHENSIVE PRE-PUSH VALIDATION
============================================================

1. Checking file syntax and imports...
   ✅ app/services/blind_overlay_service.py
   ✅ app/services/window_detection_service.py
   ...

2. Testing imports...
   ✅ All critical imports work

3. Running test suite...
   ✅ All tests pass

============================================================
✅ ALL CHECKS PASSED - Safe to push!
```

## Common Errors Caught

- ❌ `Uses 'os' but missing 'import os'`
- ❌ `Uses 'Path' but missing 'from pathlib import Path'`
- ❌ `Syntax error: ...`
- ❌ `Import test failed: ...`
- ❌ `Some tests failed`

## Best Practice

**Always run this before pushing!** It takes ~30 seconds and saves hours of debugging deployment errors.

