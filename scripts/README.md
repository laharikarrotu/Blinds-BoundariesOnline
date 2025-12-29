# Scripts Directory

Utility scripts for development, testing, and deployment.

## Available Scripts

### Development
- **`start_server.sh`** - Start backend server (kills existing process on port 8000)
- **`start_all.sh`** - Start both backend and frontend

### Testing
- **`test_tryon_comprehensive.py`** - Comprehensive try-on feature testing
- **`test_local_tryon.py`** - Local API testing script

### Code Quality
- **`pre_push_check.py`** - Pre-push validation (syntax, imports, tests)

## Usage

### Start Backend
```bash
./scripts/start_server.sh
```

### Start Both Backend and Frontend
```bash
./scripts/start_all.sh
```

### Run Tests
```bash
python3 scripts/test_tryon_comprehensive.py
python3 scripts/test_local_tryon.py
```

### Pre-Push Check
```bash
python3 scripts/pre_push_check.py
```
