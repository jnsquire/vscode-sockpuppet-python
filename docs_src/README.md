# Documentation Generation

This directory contains the automated documentation generation setup for VSCode Sockpuppet.

## Overview

The documentation is built using:
- **[MkDocs](https://www.mkdocs.org/)** - Static site generator
- **[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)** - Beautiful theme
- **[mkdocstrings](https://mkdocstrings.github.io/)** - Automatic API reference from docstrings

## Quick Start

### Install Dependencies

```bash
# Using uv
uv pip install -e ".[docs]"

# Or using pip
pip install -e ".[docs]"
```

### Build and Serve Locally

```bash
# Serve with live reload (http://127.0.0.1:8000)
mkdocs serve

# Build static site to site/ directory
mkdocs build

# Build and open in browser
mkdocs serve --open
```

## Directory Structure

```
python/
├── mkdocs.yml              # MkDocs configuration
├── docs_src/               # Documentation source files
│   ├── index.md           # Homepage
│   ├── api/               # API reference (auto-generated from docstrings)
│   ├── getting-started/   # Tutorials and guides
│   ├── guides/            # Developer guides
│   └── about/             # About pages
└── site/                  # Generated site (git-ignored)
```

## How It Works

### Automatic API Documentation

The API reference pages use mkdocstrings to automatically extract documentation from Python docstrings:

```markdown
# Window

::: vscode_sockpuppet.window.Window
```

This single line automatically generates complete documentation for the `Window` class, including:
- Class description
- All methods with signatures
- Parameter descriptions
- Return types
- Examples from docstrings

### Configuration

All mkdocstrings options are configured globally in `mkdocs.yml`:

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true
            # ... other options
```

This means you don't need to repeat options in each `.md` file.

### Adding New API Pages

To document a new module:

1. Create a new file in `docs_src/api/`:
   ```markdown
   # MyModule
   
   Description of the module.
   
   ::: vscode_sockpuppet.mymodule.MyClass
   ```

2. Add it to the navigation in `mkdocs.yml`:
   ```yaml
   nav:
     - API Reference:
       - MyModule: api/mymodule.md
   ```

3. That's it! The documentation is generated automatically.

## Customization

### Per-Page Options

While global options are set in `mkdocs.yml`, you can override them per-page:

```markdown
::: vscode_sockpuppet.window.Window
    options:
      show_source: false  # Hide source for this class
      members_order: alphabetical  # Override default ordering
```

### Filtering Members

Show only specific members:

```markdown
::: vscode_sockpuppet.window.Window
    options:
      members:
        - show_information_message
        - show_warning_message
```

### Hiding Private Members

Already configured globally, but you can control it:

```markdown
::: vscode_sockpuppet.client.VSCodeClient
    options:
      filters:
        - "!^_"  # Hide private members
```

## Docstring Style

We use **Google-style docstrings** throughout the codebase:

```python
def show_message(self, message: str, *items: str) -> Optional[str]:
    """
    Show an information message.
    
    Args:
        message: The message to show
        *items: Optional items to show as buttons
    
    Returns:
        The selected item or None if dismissed
    
    Example:
        ```python
        result = window.show_information_message(
            "Save changes?",
            "Yes", "No", "Cancel"
        )
        if result == "Yes":
            save_file()
        ```
    """
```

## Publishing

### GitHub Pages

To deploy to GitHub Pages:

```bash
mkdocs gh-deploy
```

This builds the site and pushes to the `gh-pages` branch.

### Manual Hosting

Build the site and host the `site/` directory:

```bash
mkdocs build
# Upload site/ directory to your web server
```

## Tips

1. **Live Reload**: Use `mkdocs serve` during development to see changes instantly
2. **Docstring Quality**: Good docstrings = good docs! Include examples when possible
3. **Type Hints**: Type hints automatically appear in the documentation
4. **Code Blocks**: Use triple backticks with language for syntax highlighting
5. **Admonitions**: Use `!!! note` or `!!! warning` for callouts

## Common Tasks

### Update API Reference

Just update the docstrings in the Python source code. The docs rebuild automatically.

### Add a Tutorial

1. Create a new `.md` file in `docs_src/getting-started/`
2. Add it to `nav` in `mkdocs.yml`
3. Write in Markdown with code examples

### Change Theme Colors

Edit `mkdocs.yml`:

```yaml
theme:
  palette:
    primary: indigo  # Change to: blue, red, green, etc.
    accent: indigo
```

### Add Search

Already enabled! The search plugin is configured in `mkdocs.yml`.

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings Documentation](https://mkdocstrings.github.io/)
- [Markdown Guide](https://www.markdownguide.org/)
