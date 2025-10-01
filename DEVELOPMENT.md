# Development Guide

This guide explains how to set up a development environment for the VSCode Sockpuppet Python package.

## Prerequisites

- Python 3.8 or later
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Installing uv

uv is a fast Python package installer and resolver written in Rust. It's significantly faster than pip and provides better dependency resolution.

### Installation

**Unix/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (via pip):**
```bash
pip install uv
```

## Setting up Development Environment

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/jnsquire/vscode-sockpuppet-python.git
cd vscode-sockpuppet-python

# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate  # Windows

# Install in development mode with dev dependencies
uv pip install -e ".[dev]"

# On Windows, also install platform-specific dependencies
uv pip install -e ".[windows]"
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/jnsquire/vscode-sockpuppet-python.git
cd vscode-sockpuppet-python

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate  # Windows

# Install in development mode
pip install -e ".[dev]"

# On Windows
pip install -e ".[windows]"
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vscode_sockpuppet --cov-report=html

# Run specific test file
pytest tests/test_client.py -v
```

### Code Quality

#### Linting with ruff

```bash
# Install ruff
uv pip install ruff

# Check for issues
ruff check vscode_sockpuppet

# Fix auto-fixable issues
ruff check --fix vscode_sockpuppet
```

#### Formatting with ruff

```bash
# Check formatting
ruff format --check vscode_sockpuppet

# Format code
ruff format vscode_sockpuppet
```

#### Type Checking with mypy

```bash
# Run type checking
mypy vscode_sockpuppet --ignore-missing-imports
```

### Running Examples

Make sure the VS Code extension is running first:

```bash
# Basic example
python examples/example.py

# Document API example
python examples/example_document.py

# Event subscriptions example
python examples/example_events.py

# Webview example
python examples/example_webview.py
```

## Project Structure

```
vscode-sockpuppet-python/
├── .github/
│   └── workflows/
│       └── test.yml          # CI/CD pipeline
├── vscode_sockpuppet/
│   ├── __init__.py          # Package exports
│   ├── client.py            # Main client class
│   ├── document.py          # TextDocument API
│   ├── editor.py            # Editor operations
│   ├── webview.py           # Webview API
│   ├── window.py            # Window operations
│   └── workspace.py         # Workspace operations
├── examples/                # Example scripts
│   ├── example.py           # Basic operations
│   ├── example_document.py  # TextDocument API
│   ├── example_events.py    # Event subscriptions
│   └── example_webview.py   # Webview API
├── tests/                   # Test files (to be added)
├── pyproject.toml           # Project configuration
├── .python-version          # Python version for uv
└── README.md               # Package documentation
```

## Building and Publishing

### Building the Package

```bash
# Install build tool
uv pip install build

# Build distribution packages
python -m build

# Output will be in dist/
# - vscode-sockpuppet-0.1.0.tar.gz
# - vscode_sockpuppet-0.1.0-py3-none-any.whl
```

### Publishing to PyPI

```bash
# Install twine
uv pip install twine

# Upload to TestPyPI (for testing)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

## Code Style Guidelines

### Python Version Support

- Minimum: Python 3.8
- Target: Python 3.8, 3.9, 3.10, 3.11, 3.12
- Use type hints compatible with Python 3.8

### Code Style

- **Line Length:** 79 characters (PEP 8)
- **Formatter:** ruff (compatible with black)
- **Linter:** ruff (replaces flake8)
- **Type Checker:** mypy with strict mode
- **Docstrings:** Google style

### Example

```python
"""
Module docstring.
"""

from typing import Optional


def example_function(param: str, optional: Optional[int] = None) -> bool:
    """
    Short description.
    
    Longer description if needed.
    
    Args:
        param: Description of param
        optional: Description of optional param
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something goes wrong
    """
    if not param:
        raise ValueError("param cannot be empty")
    
    return True
```

## Adding Dependencies

### Runtime Dependencies

Add to `pyproject.toml` under `[project.dependencies]`:

```toml
[project]
dependencies = [
    "requests>=2.28.0",  # Add new dependency
]
```

Then reinstall:
```bash
uv pip install -e .
```

### Development Dependencies

Add to `[project.optional-dependencies.dev]`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",  # Add new dev dependency
]
```

Then reinstall:
```bash
uv pip install -e ".[dev]"
```

## Continuous Integration

The project uses GitHub Actions for CI/CD:

- **Test Matrix:** Python 3.8-3.12 on Ubuntu, Windows, macOS
- **Linting:** ruff check and format
- **Type Checking:** mypy
- **Coverage:** pytest with codecov upload

The CI workflow uses `uv` for faster dependency installation.

## Troubleshooting

### uv is not found

Make sure uv is installed and in your PATH:
```bash
# Check installation
uv --version

# Reinstall if needed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Import errors

Make sure the package is installed in editable mode:
```bash
uv pip install -e .
```

### VS Code connection errors

1. Make sure the VS Code extension is running
2. Check the named pipe path:
   - Windows: `\\.\pipe\vscode-sockpuppet`
   - Unix: `/tmp/vscode-sockpuppet.sock`

### Platform-specific issues

On Windows, install the Windows-specific dependencies:
```bash
uv pip install -e ".[windows]"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [VS Code Extension API](https://code.visualstudio.com/api)
