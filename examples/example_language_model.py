"""
Example: Using Language Model API (Copilot) for AI-powered automation

This example demonstrates how to interact with VS Code's language models
(like GitHub Copilot) to create AI-powered automation workflows.
"""

from vscode_sockpuppet import LanguageModelChatMessage, VSCodeClient

# Connect to VS Code
client = VSCodeClient()
client.connect()

print("Language Model API Examples")
print("=" * 70)

# Example 1: List available models
print("\n1. Available Language Models:")
print("-" * 70)

try:
    # Get all available models
    all_models = client.lm.select_chat_models()

    if not all_models:
        print("⚠️  No language models available.")
        print("   Make sure GitHub Copilot or another LM provider is installed")
        print("   and you're signed in.")
        exit(1)

    for model in all_models:
        print(f"\nModel: {model.name}")
        print(f"  ID:               {model.id}")
        print(f"  Vendor:           {model.vendor}")
        print(f"  Family:           {model.family}")
        print(f"  Version:          {model.version}")
        print(f"  Max Input Tokens: {model.max_input_tokens:,}")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTo use this feature, you need:")
    print("  1. GitHub Copilot extension installed")
    print("  2. Active Copilot subscription")
    print("  3. Signed in to GitHub")
    exit(1)

# Example 2: Simple chat request
print("\n\n2. Simple Chat Request:")
print("-" * 70)

# Get a Copilot model
models = client.lm.select_chat_models(vendor="copilot")
if models:
    model = models[0]

    # Send a simple request
    messages = [
        LanguageModelChatMessage.user("Explain what async/await does in Python in one sentence.")
    ]

    print(f"Question: {messages[0].content}")
    print(f"\nAsking {model.name}...\n")

    response = model.send_request(messages)
    print(f"Response: {response['text']}")

# Example 3: Code explanation workflow
print("\n\n3. Code Explanation Workflow:")
print("-" * 70)

# Get the active editor's selected code
try:
    selection = client.editor.get_selection()
    selected_text = selection.get("text", "")

    if selected_text.strip():
        print(f"Selected code:\n{selected_text}\n")

        # Ask the model to explain it
        messages = [
            LanguageModelChatMessage.user(f"Explain this code concisely:\n\n{selected_text}")
        ]

        response = model.send_request(messages)
        explanation = response["text"]

        print(f"Explanation:\n{explanation}\n")

        # Show the explanation in VS Code
        client.window.show_information_message(f"Code Explanation:\n\n{explanation[:200]}...")
    else:
        print("No code selected. Select some code and run again.")
except Exception as e:
    print(f"No active editor or selection. Error: {e}")

# Example 4: Multi-turn conversation
print("\n\n4. Multi-turn Conversation:")
print("-" * 70)

messages = [
    LanguageModelChatMessage.user("What is a Python decorator?"),
]

print(f"User: {messages[0].content}")
response = model.send_request(messages)
assistant_response = response["text"]
print(f"\nAssistant: {assistant_response}")

# Add assistant response to conversation history
messages.append(LanguageModelChatMessage.assistant(assistant_response))

# Ask a follow-up question
messages.append(LanguageModelChatMessage.user("Can you show me a simple example?"))

print(f"\nUser: {messages[2].content}")
response = model.send_request(messages)
print(f"\nAssistant: {response['text']}")

# Example 5: Token counting
print("\n\n5. Token Counting:")
print("-" * 70)

test_texts = [
    "Hello, world!",
    "This is a longer piece of text with multiple sentences. "
    "It contains more words and should use more tokens.",
    "def fibonacci(n):\n    if n <= 1:\n        return n\n    "
    "return fibonacci(n-1) + fibonacci(n-2)",
]

for text in test_texts:
    token_count = model.count_tokens(text)
    print(f"\nText: {text[:50]}{'...' if len(text) > 50 else ''}")
    print(f"Tokens: {token_count}")

# Example 6: Code generation with specific options
print("\n\n6. Code Generation with Options:")
print("-" * 70)

messages = [
    LanguageModelChatMessage.user(
        "Write a Python function to check if a number is prime. Include docstring and type hints."
    )
]

# You can pass options like temperature (not all models support all options)
response = model.send_request(messages, options={})
generated_code = response["text"]

print("Generated Code:")
print(generated_code)

# Example 7: Error explanation and fix suggestion
print("\n\n7. Error Analysis:")
print("-" * 70)

error_code = """
def divide(a, b):
    return a / b

result = divide(10, 0)
"""

error_message = "ZeroDivisionError: division by zero"

messages = [
    LanguageModelChatMessage.user(
        f"This code produces an error:\n\n{error_code}\n\n"
        f"Error: {error_message}\n\n"
        f"Explain the error and suggest a fix."
    )
]

response = model.send_request(messages)
analysis = response["text"]

print(f"Code:\n{error_code}")
print(f"\nError: {error_message}")
print(f"\nAnalysis:\n{analysis}")

# Example 8: Using specific model families
print("\n\n8. Model Selection:")
print("-" * 70)

# Try to get a specific model family (e.g., GPT-4)
try:
    gpt4_models = client.lm.select_chat_models(vendor="copilot", family="gpt-4o")

    if gpt4_models:
        print(f"Found GPT-4 model: {gpt4_models[0].name}")
        print(f"Max tokens: {gpt4_models[0].max_input_tokens:,}")
    else:
        print("GPT-4 model not available, using default model")

except Exception as e:
    print(f"Could not get specific model: {e}")

# Example 9: Practical use case - Documentation generator
print("\n\n9. Documentation Generator:")
print("-" * 70)

function_code = """
def calculate_total(items, tax_rate=0.08, discount=0):
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    discount_amount = subtotal * discount
    taxable = subtotal - discount_amount
    tax = taxable * tax_rate
    return taxable + tax
"""

messages = [
    LanguageModelChatMessage.user(
        f"Generate comprehensive docstring for this Python function:\n\n"
        f"{function_code}\n\n"
        f"Include: description, args, returns, and an example."
    )
]

response = model.send_request(messages)
docstring = response["text"]

print(f"Original function:\n{function_code}")
print(f"\nGenerated documentation:\n{docstring}")

print("\n" + "=" * 70)
print("✅ Language Model API examples completed!")
print("\nKey capabilities:")
print("  • Select available language models")
print("  • Send chat requests with conversation history")
print("  • Count tokens for cost estimation")
print("  • Generate code, explanations, and documentation")
print("  • Multi-turn conversations with context")
print("  • Integrate AI into VS Code automation workflows")

client.disconnect()
