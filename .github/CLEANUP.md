# Project Cleanup Guide

## Automatic Cleanup

Run this before committing to git:

```bash
# Remove all __pycache__ directories
Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Remove .pyc files
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force

# Remove backup files
Get-ChildItem -Path . -Recurse -Filter "*.bak" | Remove-Item -Force

# Remove build folder (PyInstaller temporary)
if (Test-Path "build") { Remove-Item -Path "build" -Recurse -Force }

# Remove test files (optional)
Get-ChildItem -Path . -Recurse -Filter "test_*.py" | Where-Object { $_.Name -ne "tests.py" } | Remove-Item -Force
```

## Files to Keep

### Essential Files
- `manage.py` - Django CLI
- `agent.py` - Agent source
- `agent.spec` - PyInstaller config
- `db.sqlite3` - Database
- `README.md` - Documentation
- `LICENSE` - License file
- `requirements.txt` - Dependencies
- `CONTRIBUTING.md` - Guidelines
- `.env.template` - Config template
- `.gitignore` - Git rules

### Folders to Keep
- `monitor/` - Main application
- `server_509/` - Django config
- `dist/` - Compiled agent
- `logs/` - Log files (gitignored)
- `venv_win/` - Virtual env (gitignored)
- `.github/` - GitHub config

## Files to Remove

### Temporary Files
- `__pycache__/` directories
- `*.pyc` files
- `*.pyo` files
- `build/` folder

### Backup Files
- `*.bak` files
- `*.backup` files
- `*.old` files
- `db.sqlite3.bak`

### Test Files
- `test_*.py` (except `tests.py`)
- `*_test.py`
- `debug_*.py`

## Before Git Commit

```bash
# Clean project
python -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"

# Check what will be committed
git status

# Review .gitignore
cat .gitignore
```
