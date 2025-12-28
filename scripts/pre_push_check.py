#!/usr/bin/env python3
"""
Comprehensive pre-push validation script.
Run this before pushing to catch common errors.
"""
import ast
import sys
import subprocess
from pathlib import Path

def check_file(file_path):
    """Check a single file for common issues."""
    errors = []
    warnings = []
    
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        
        # 1. Check syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")
            return errors, warnings
        
        # 2. Check for missing imports
        if 'os.' in code or 'os.path' in code or 'os.environ' in code or 'os.access' in code or 'os.exists' in code:
            if 'import os' not in code and 'from os' not in code:
                errors.append("Uses 'os' but missing 'import os'")
        
        if 'Path(' in code:
            if 'from pathlib import Path' not in code and 'import Path' not in code:
                errors.append("Uses 'Path' but missing 'from pathlib import Path'")
        
        if 'np.' in code or 'numpy' in code:
            if 'import numpy' not in code and 'import numpy as np' not in code:
                errors.append("Uses 'numpy' but missing import")
        
        if 'Image.' in code or 'PILImage' in code:
            if 'from PIL import Image' not in code and 'import Image' not in code:
                if 'PILImage' in code and 'from PIL import Image as PILImage' not in code:
                    errors.append("Uses 'PIL/Image' but missing import")
        
        if 'np.array' in code or 'np.zeros' in code:
            if 'import numpy as np' not in code:
                errors.append("Uses 'np' but missing 'import numpy as np'")
        
        # 3. Check for undefined variables (common patterns)
        if 'storage_repo' in code and 'storage_repo =' not in code and 'self.storage_repo' not in code:
            if 'def __init__' in code:
                # Might be passed as parameter, check if it's in function signature
                if 'storage_repo=None' not in code and 'storage_repo:' not in code:
                    warnings.append("Uses 'storage_repo' - verify it's defined")
        
    except FileNotFoundError:
        errors.append("File not found")
    except Exception as e:
        errors.append(f"Error checking file: {e}")
    
    return errors, warnings

def main():
    """Run comprehensive pre-push checks."""
    print("=" * 60)
    print("COMPREHENSIVE PRE-PUSH VALIDATION")
    print("=" * 60)
    print()
    
    all_errors = []
    all_warnings = []
    
    # Files to check
    files_to_check = [
        'app/services/blind_overlay_service.py',
        'app/services/window_detection_service.py',
        'app/hybrid_detector.py',
        'app/api/routes.py',
        'app/api/main.py',
        'app/repositories/image_repository.py',
        'app/repositories/mask_repository.py',
    ]
    
    print("1. Checking file syntax and imports...")
    for file_path in files_to_check:
        if not Path(file_path).exists():
            print(f"   ⚠️ {file_path} - File not found (skipping)")
            continue
        
        errors, warnings = check_file(file_path)
        if errors:
            print(f"   ❌ {file_path}:")
            for error in errors:
                print(f"      - {error}")
                all_errors.append(f"{file_path}: {error}")
        elif warnings:
            print(f"   ⚠️ {file_path}:")
            for warning in warnings:
                print(f"      - {warning}")
                all_warnings.append(f"{file_path}: {warning}")
        else:
            print(f"   ✅ {file_path}")
    
    print("\n2. Testing imports...")
    try:
        sys.path.insert(0, '.')
        from app.services.blind_overlay_service import BlindOverlayService
        from app.services.window_detection_service import WindowDetectionService
        from app.api.routes import router
        print("   ✅ All critical imports work")
    except Exception as e:
        error_msg = f"Import test failed: {e}"
        print(f"   ❌ {error_msg}")
        all_errors.append(error_msg)
    
    print("\n3. Running test suite...")
    try:
        result = subprocess.run(
            ['python3', '-m', 'pytest', 'tests/', '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("   ✅ All tests pass")
        else:
            error_msg = "Some tests failed"
            print(f"   ❌ {error_msg}")
            print(f"   Last 10 lines of output:")
            for line in result.stdout.split('\n')[-10:]:
                if line.strip():
                    print(f"      {line}")
            all_errors.append(error_msg)
    except subprocess.TimeoutExpired:
        error_msg = "Tests timed out"
        print(f"   ❌ {error_msg}")
        all_errors.append(error_msg)
    except Exception as e:
        error_msg = f"Error running tests: {e}"
        print(f"   ❌ {error_msg}")
        all_errors.append(error_msg)
    
    print("\n4. Checking for common issues...")
    # Check if all changed files are checked
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'origin/main'],
            capture_output=True,
            text=True
        )
        changed_files = [f for f in result.stdout.strip().split('\n') if f.endswith('.py')]
        unchecked = [f for f in changed_files if f not in files_to_check and f.startswith('app/')]
        if unchecked:
            print(f"   ⚠️ Some changed Python files not checked:")
            for f in unchecked:
                print(f"      - {f}")
                all_warnings.append(f"Unchecked file: {f}")
        else:
            print("   ✅ All changed Python files are checked")
    except Exception as e:
        print(f"   ⚠️ Could not check git diff: {e}")
    
    print("\n" + "=" * 60)
    if all_errors:
        print(f"❌ FOUND {len(all_errors)} ERRORS - DO NOT PUSH!")
        print("\nErrors:")
        for error in all_errors:
            print(f"  - {error}")
        print("\n⚠️ Fix these errors before pushing!")
        return 1
    else:
        print("✅ ALL CHECKS PASSED - Safe to push!")
        if all_warnings:
            print(f"\n⚠️ {len(all_warnings)} warnings (non-critical):")
            for warning in all_warnings:
                print(f"  - {warning}")
        return 0

if __name__ == "__main__":
    sys.exit(main())

