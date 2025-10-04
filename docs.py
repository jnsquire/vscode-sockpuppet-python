#!/usr/bin/env python3
"""
Documentation helper script for VSCode Sockpuppet.

Usage:
    python docs.py serve    # Serve docs with live reload
    python docs.py build    # Build static site
    python docs.py deploy   # Deploy to GitHub Pages
"""

import subprocess
import sys
from pathlib import Path

# Change to python directory
PROJECT_ROOT = Path(__file__).parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

# Use venv python if available, otherwise system python
if VENV_PYTHON.exists():
    PYTHON = str(VENV_PYTHON)
else:
    PYTHON = sys.executable


def run_command(cmd: list[str]) -> int:
    """Run a command and return exit code."""
    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130


def serve():
    """Serve documentation with live reload."""
    print("Starting documentation server...")
    print("Open http://127.0.0.1:8000 in your browser")
    print("Press Ctrl+C to stop\n")
    return run_command([PYTHON, "-m", "mkdocs", "serve"])


def build():
    """Build static documentation site."""
    print("Building documentation...")
    code = run_command([PYTHON, "-m", "mkdocs", "build", "--clean"])
    if code == 0:
        print("\nDocumentation built successfully!")
        print(f"Output: {PROJECT_ROOT / 'site'}")
    return code


def deploy():
    """Deploy documentation to GitHub Pages."""
    print("Deploying to GitHub Pages...")
    code = run_command([PYTHON, "-m", "mkdocs", "gh-deploy"])
    if code == 0:
        print("\nDocumentation deployed successfully!")
    return code


def main():
    """Main entry point."""
    commands = {
        "serve": serve,
        "build": build,
        "deploy": deploy,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print(__doc__)
        print(f"\nAvailable commands: {', '.join(commands.keys())}")
        return 1

    command = sys.argv[1]
    return commands[command]()


if __name__ == "__main__":
    sys.exit(main())
