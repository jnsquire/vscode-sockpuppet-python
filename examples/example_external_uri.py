"""
Example: Using env.as_external_uri() to convert URIs

This example demonstrates converting internal URIs to external URIs,
which is particularly useful when VS Code is running in remote contexts
like SSH, WSL, or Codespaces where localhost needs to be tunneled.
"""

from vscode_sockpuppet import VSCodeClient

# Connect to VS Code
client = VSCodeClient()

print("Environment URI Conversion Examples")
print("=" * 60)

# Example 1: Convert a localhost URI
# This is useful when running a dev server and you need the public URL
localhost_uri = "http://localhost:3000"
external_uri = client.workspace.env.as_external_uri(localhost_uri)
print(f"\nLocalhost URI: {localhost_uri}")
print(f"External URI:  {external_uri}")

# Example 2: Convert localhost with path
dev_server = "http://localhost:8080/api/docs"
external_dev = client.workspace.env.as_external_uri(dev_server)
print(f"\nDev Server:    {dev_server}")
print(f"External URL:  {external_dev}")

# Example 3: Convert workspace file URI
# Get current workspace folder
folders = client.workspace.get_workspace_folders()
if folders:
    workspace_uri = folders[0]["uri"]
    file_uri = f"{workspace_uri}/README.md"
    external_file = client.workspace.env.as_external_uri(file_uri)
    print(f"\nFile URI:      {file_uri}")
    print(f"External URI:  {external_file}")

# Example 4: Combined with open_external
# Convert and open a localhost URL in browser
print("\n" + "=" * 60)
print("Converting and opening in browser...")
local_url = "http://localhost:5000"
external_url = client.workspace.env.as_external_uri(local_url)
print(f"Opening: {external_url}")
client.workspace.env.open_external(external_url)

# Example 5: Use case - Starting a dev server and sharing the URL
print("\n" + "=" * 60)
print("Use Case: Dev Server with Public URL")
print("=" * 60)

# Simulate starting a server (you would actually start your server here)
server_port = 8000
local_server = f"http://localhost:{server_port}"

# Convert to external URI for sharing
public_url = client.workspace.env.as_external_uri(local_server)

# Show information message with the public URL
choice = client.window.show_information_message(
    f"Dev server running at:\n{public_url}", "Copy URL", "Open in Browser"
)

# Handle user choice
if choice == "Copy URL":
    client.workspace.env.write_clipboard(public_url)
    client.window.show_information_message("URL copied to clipboard!")
elif choice == "Open in Browser":
    client.workspace.env.open_external(public_url)

print(f"\nLocal Server:  {local_server}")
print(f"Public URL:    {public_url}")
print("\nℹ️  When VS Code is running locally, these URIs will be the same.")
print("   When running remotely (SSH/WSL/Codespaces), the external URI")
print("   will be tunneled through VS Code's port forwarding.")
