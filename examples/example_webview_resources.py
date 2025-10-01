"""
Example: Using webview with local file resources

Demonstrates how to use asWebviewUri to load local images, CSS, and
JavaScript files in a webview panel.
"""

import os
import time

from vscode_sockpuppet import VSCodeClient, WebviewOptions


def create_html_with_resources(panel, workspace_path: str) -> str:
    """
    Create HTML that references local resources.

    Args:
        panel: The webview panel
        workspace_path: Path to the workspace folder

    Returns:
        HTML string with webview URIs for local resources
    """
    # Example: Convert local file paths to webview URIs
    # In a real scenario, these would be actual files in your workspace

    # Convert workspace path to file URI format
    if not workspace_path.startswith("file://"):
        workspace_uri = f"file:///{workspace_path.replace(os.sep, '/')}"
    else:
        workspace_uri = workspace_path

    # Example paths (these would be real files in practice)
    # For demonstration, we'll show the pattern
    css_uri = panel.as_webview_uri(f"{workspace_uri}/styles/main.css")
    js_uri = panel.as_webview_uri(f"{workspace_uri}/scripts/app.js")
    img_uri = panel.as_webview_uri(f"{workspace_uri}/images/logo.png")

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Webview with Resources</title>

        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                padding: 20px;
                background-color: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground);
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
            }}
            h1 {{
                color: var(--vscode-textLink-foreground);
            }}
            .uri-example {{
                background-color: var(--vscode-editor-selectionBackground);
                padding: 10px;
                margin: 10px 0;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                word-break: break-all;
            }}
            .label {{
                color: var(--vscode-descriptionForeground);
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .note {{
                padding: 15px;
                margin: 20px 0;
                border-left: 4px solid var(--vscode-editorWarning-foreground);
                background-color: var(--vscode-inputValidation-warningBackground);
                color: var(--vscode-inputValidation-warningForeground);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔒 Webview with Local Resources</h1>

            <p>
                This example demonstrates how to use <code>as_webview_uri()</code>
                to convert local file URIs into webview-safe URIs.
            </p>

            <div class="note">
                <strong>Note:</strong> Webviews cannot directly access local files
                using file:// URIs for security reasons. The <code>asWebviewUri</code>
                method converts local file paths into special webview URIs that VS Code
                will serve securely.
            </div>

            <h2>Example URI Conversions</h2>

            <div class="label">CSS File:</div>
            <div class="uri-example">{css_uri}</div>

            <div class="label">JavaScript File:</div>
            <div class="uri-example">{js_uri}</div>

            <div class="label">Image File:</div>
            <div class="uri-example">{img_uri}</div>

            <h2>How to Use</h2>

            <ol>
                <li>
                    Create a webview with <code>localResourceRoots</code> specified:
                    <pre style="background-color: var(--vscode-editor-selectionBackground);
                                padding: 10px; border-radius: 3px;">
# Specify which directories can be accessed
options = WebviewOptions(
    enable_scripts=True,
    local_resource_roots=[workspace_uri]
)
                    </pre>
                </li>
                <li>
                    Convert local file URIs to webview URIs:
                    <pre style="background-color: var(--vscode-editor-selectionBackground);
                                padding: 10px; border-radius: 3px;">
# Convert local URI
css_uri = panel.as_webview_uri('file:///path/to/style.css')
                    </pre>
                </li>
                <li>
                    Use the converted URIs in your HTML:
                    <pre style="background-color: var(--vscode-editor-selectionBackground);
                                padding: 10px; border-radius: 3px;">
html = f'&lt;link rel="stylesheet" href="{{css_uri}}"&gt;'
                    </pre>
                </li>
            </ol>

            <h2>Security Considerations</h2>

            <ul>
                <li>
                    Only files within <code>localResourceRoots</code> can be accessed
                </li>
                <li>
                    Always use a Content Security Policy (CSP) to restrict what
                    resources can be loaded
                </li>
                <li>
                    Sanitize any user-provided content before including it in the webview
                </li>
            </ul>

            <p style="margin-top: 30px; color: var(--vscode-descriptionForeground);">
                <em>Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}</em>
            </p>
        </div>
    </body>
    </html>
    """

    return html


def example_basic_uri_conversion(client: VSCodeClient):
    """Example 1: Basic URI conversion."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic URI Conversion")
    print("=" * 70)

    # Get workspace folder
    folders = client.workspace.get_workspace_folders()
    if not folders:
        print("   No workspace folder open")
        return

    workspace_path = folders[0]["uri"]
    print(f"\n   Workspace: {workspace_path}")

    # Create webview with local resource roots
    options = WebviewOptions(
        enable_scripts=True,
        local_resource_roots=[workspace_path],
    )

    panel = client.window.create_webview_panel(
        view_type="resourceDemo",
        title="Webview Resources Demo",
        html="",
        options=options,
    )

    print(f"   Created webview panel: {panel.id}")

    # Convert some example URIs
    print("\n   Converting local URIs to webview URIs:")

    example_paths = [
        f"{workspace_path}/README.md",
        f"{workspace_path}/package.json",
        f"{workspace_path}/src/extension.ts",
    ]

    for path in example_paths:
        try:
            webview_uri = panel.as_webview_uri(path)
            print(f"\n   Local:   {path}")
            print(f"   Webview: {webview_uri}")
        except Exception as e:
            print(f"   Error converting {path}: {e}")

    # Set the HTML content
    html = create_html_with_resources(panel, workspace_path)
    panel.update_html(html)

    print("\n   Webview panel created with resource examples!")
    print("   Check the webview to see the URI conversions.")

    time.sleep(5)
    panel.dispose()
    print("   Panel disposed")


def example_image_loading(client: VSCodeClient):
    """Example 2: Loading local images in webview."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Loading Local Images")
    print("=" * 70)

    folders = client.workspace.get_workspace_folders()
    if not folders:
        print("   No workspace folder open")
        return

    workspace_path = folders[0]["uri"]

    # Create webview
    options = WebviewOptions(
        enable_scripts=True,
        local_resource_roots=[workspace_path],
    )

    panel = client.window.create_webview_panel(
        view_type="imageDemo",
        title="Image Loading Demo",
        html="",
        options=options,
    )

    # Create HTML with image references
    # Note: In practice, you'd reference actual image files
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                padding: 20px;
                background-color: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground);
            }
            .gallery {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .image-card {
                border: 1px solid var(--vscode-panel-border);
                border-radius: 5px;
                padding: 10px;
            }
        </style>
    </head>
    <body>
        <h1>📸 Local Image Loading</h1>
        <p>
            To load local images, use <code>as_webview_uri()</code> to convert
            file paths to webview-safe URIs.
        </p>

        <h2>Example Pattern:</h2>
        <pre style="background: var(--vscode-editor-selectionBackground);
                    padding: 10px; border-radius: 3px;">
# Python code:
img_path = 'file:///path/to/image.png'
img_uri = panel.as_webview_uri(img_path)

html = f'&lt;img src="{img_uri}" alt="My Image"&gt;'
panel.update_html(html)
        </pre>

        <p style="margin-top: 30px;">
            <em>Note: Make sure image files are within the localResourceRoots
            directory specified when creating the webview.</em>
        </p>
    </body>
    </html>
    """

    panel.update_html(html)
    print("   Image loading demo created!")

    time.sleep(5)
    panel.dispose()
    print("   Panel disposed")


def example_css_js_loading(client: VSCodeClient):
    """Example 3: Loading CSS and JavaScript files."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Loading CSS and JavaScript")
    print("=" * 70)

    folders = client.workspace.get_workspace_folders()
    if not folders:
        print("   No workspace folder open")
        return

    workspace_path = folders[0]["uri"]

    options = WebviewOptions(
        enable_scripts=True,
        local_resource_roots=[workspace_path],
    )

    panel = client.window.create_webview_panel(
        view_type="cssJsDemo",
        title="CSS/JS Loading Demo",
        html="",
        options=options,
    )

    # Example showing how to load external CSS and JS
    # In practice, these would be real files
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                padding: 20px;
                background-color: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            pre {
                background-color: var(--vscode-editor-selectionBackground);
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            code {
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <h1>🎨 Loading CSS and JavaScript Files</h1>

        <h2>Loading External CSS:</h2>
        <pre><code>css_uri = panel.as_webview_uri('file:///path/to/style.css')
html = f'&lt;link rel="stylesheet" href="{css_uri}"&gt;'</code></pre>

        <h2>Loading External JavaScript:</h2>
        <pre><code>js_uri = panel.as_webview_uri('file:///path/to/script.js')
html = f'&lt;script src="{js_uri}"&gt;&lt;/script&gt;'</code></pre>

        <h2>Complete Example:</h2>
        <pre><code># Python code
workspace_uri = 'file:///Users/name/project'
options = WebviewOptions(
    enable_scripts=True,
    local_resource_roots=[workspace_uri]
)

panel = client.window.create_webview_panel(
    title="My Webview",
    options=options
)

# Convert file URIs
css_uri = panel.as_webview_uri(f'{workspace_uri}/styles/main.css')
js_uri = panel.as_webview_uri(f'{workspace_uri}/scripts/app.js')

# Build HTML
html = f'''
&lt;link rel="stylesheet" href="{css_uri}"&gt;
&lt;script src="{js_uri}"&gt;&lt;/script&gt;
'''

panel.update_html(html)</code></pre>
    </body>
    </html>
    """

    panel.update_html(html)
    print("   CSS/JS loading demo created!")

    time.sleep(5)
    panel.dispose()
    print("   Panel disposed")


def main():
    """Run all webview resource examples."""
    print("Webview Resource Loading Examples")
    print("=" * 70)
    print("Demonstrates using asWebviewUri to load local resources")

    client = VSCodeClient()
    client.connect()

    try:
        folders = client.workspace.get_workspace_folders()
        if not folders:
            print("\n❌ No workspace folder open")
            print("   Please open a folder in VS Code first")
            return

        print("\n✓ Connected to VS Code")
        print(f"✓ Workspace: {folders[0]['name']}")

        # Run examples
        example_basic_uri_conversion(client)
        time.sleep(1)

        example_image_loading(client)
        time.sleep(1)

        example_css_js_loading(client)

        print("\n" + "=" * 70)
        print("Examples completed!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
