# Language Model API

Access VS Code's Language Model API to interact with GitHub Copilot and other AI models directly from Python.

## Overview

The Language Model API enables Python scripts to:
- **Query available language models** (Copilot, custom providers)
- **Send chat requests** with conversation history
- **Generate code, documentation, and explanations**
- **Count tokens** for cost estimation
- **Build AI-powered automation workflows**

::: vscode_sockpuppet.language_model.LanguageModel

::: vscode_sockpuppet.language_model.LanguageModelChat

::: vscode_sockpuppet.language_model.LanguageModelChatMessage

## Usage Examples

### Basic Chat Request

```python
from vscode_sockpuppet import VSCodeClient, LanguageModelChatMessage

client = VSCodeClient()
client.connect()

# Get available models
models = client.lm.select_chat_models(vendor='copilot')
model = models[0]

# Send a request
messages = [
    LanguageModelChatMessage.user("Explain async/await in Python")
]

response = model.send_request(messages)
print(response['text'])
```

### Multi-turn Conversation

```python
# Start conversation
messages = [
    LanguageModelChatMessage.user("What is a Python decorator?")
]

response = model.send_request(messages)
print(f"Assistant: {response['text']}")

# Add response to history
messages.append(
    LanguageModelChatMessage.assistant(response['text'])
)

# Ask follow-up
messages.append(
    LanguageModelChatMessage.user("Show me an example")
)

response = model.send_request(messages)
print(f"Assistant: {response['text']}")
```

### Code Generation

```python
messages = [
    LanguageModelChatMessage.user(
        "Write a Python function to check if a number is prime. "
        "Include docstring and type hints."
    )
]

response = model.send_request(messages)
generated_code = response['text']
print(generated_code)
```

### Token Counting

```python
# Count tokens before sending
text = "This is a long piece of text..."
token_count = model.count_tokens(text)
print(f"This will use approximately {token_count} tokens")

# Helpful for estimating costs and staying within limits
if token_count < model.max_input_tokens:
    response = model.send_request([
        LanguageModelChatMessage.user(text)
    ])
```

### Code Explanation Workflow

```python
# Get selected code from active editor
editor = client.editor.get_active_text_editor()
if editor and editor.selection:
    doc = client.workspace.open_text_document(editor.document['uri'])
    selected_text = doc.get_text_range(editor.selection)
    
    # Ask model to explain
    messages = [
        LanguageModelChatMessage.user(
            f"Explain this code:\n\n{selected_text}"
        )
    ]
    
    response = model.send_request(messages)
    
    # Show explanation in VS Code
    client.window.show_information_message(
        f"Explanation: {response['text'][:200]}..."
    )
```

### Error Analysis

```python
error_code = """
def divide(a, b):
    return a / b
"""

error_message = "ZeroDivisionError: division by zero"

messages = [
    LanguageModelChatMessage.user(
        f"This code has an error:\n\n{error_code}\n\n"
        f"Error: {error_message}\n\n"
        "Explain the problem and suggest a fix."
    )
]

response = model.send_request(messages)
print(response['text'])
```

### Model Selection

```python
# Get all available models
all_models = client.lm.select_chat_models()
for model in all_models:
    print(f"{model.name}: {model.max_input_tokens:,} tokens")

# Get specific vendor
copilot_models = client.lm.select_chat_models(vendor='copilot')

# Get specific model family
gpt4_models = client.lm.select_chat_models(
    vendor='copilot',
    family='gpt-4o'
)

# Get by exact ID
specific = client.lm.select_chat_models(
    id='copilot-gpt-4o'
)
```

## Requirements

### GitHub Copilot

To use the Language Model API with Copilot:

1. **Install** the GitHub Copilot extension in VS Code
2. **Sign in** to your GitHub account
3. **Have an active** Copilot subscription

### Custom Language Model Providers

VS Code's Language Model API supports custom providers. Any extension that
implements the `LanguageModelChatProvider` interface will be accessible
through this API.

## Error Handling

```python
try:
    models = client.lm.select_chat_models(vendor='copilot')
    
    if not models:
        print("No models available - is Copilot installed?")
        exit(1)
    
    model = models[0]
    response = model.send_request(messages)
    
except Exception as e:
    if "LanguageModelError" in str(e):
        print(f"Language model error: {e}")
        # Could be: model not found, user consent not given,
        # quota exceeded, content filtered, etc.
    else:
        print(f"Unexpected error: {e}")
```

## Best Practices

### 1. Check Model Availability

```python
models = client.lm.select_chat_models(vendor='copilot')
if not models:
    client.window.show_warning_message(
        "Copilot not available. Please sign in and try again."
    )
    exit(1)
```

### 2. Handle Conversation Context

```python
# Keep conversation history for context
conversation = []

def ask(question: str) -> str:
    conversation.append(LanguageModelChatMessage.user(question))
    response = model.send_request(conversation)
    answer = response['text']
    conversation.append(LanguageModelChatMessage.assistant(answer))
    return answer
```

### 3. Stay Within Token Limits

```python
# Check if prompt fits within limits
prompt_tokens = model.count_tokens(user_prompt)
if prompt_tokens > model.max_input_tokens:
    print(f"Prompt too long! {prompt_tokens}/{model.max_input_tokens}")
    # Truncate or split the prompt
```

### 4. Provide Clear Instructions

```python
# Be specific in your requests
messages = [
    LanguageModelChatMessage.user(
        "Write a Python function that:\n"
        "1. Takes a list of numbers\n"
        "2. Returns only the even numbers\n"
        "3. Includes type hints\n"
        "4. Has a docstring with an example\n"
        "5. Uses list comprehension"
    )
]
```

## Use Cases

### Documentation Generation

Generate docstrings, comments, and README content:

```python
def generate_docstring(function_code: str) -> str:
    messages = [
        LanguageModelChatMessage.user(
            f"Generate a comprehensive Google-style docstring "
            f"for this function:\n\n{function_code}"
        )
    ]
    response = model.send_request(messages)
    return response['text']
```

### Code Review Assistant

Analyze code for issues and suggestions:

```python
def review_code(code: str) -> str:
    messages = [
        LanguageModelChatMessage.user(
            f"Review this code for:\n"
            f"- Potential bugs\n"
            f"- Performance issues\n"
            f"- Best practices\n\n"
            f"{code}"
        )
    ]
    response = model.send_request(messages)
    return response['text']
```

### Test Generation

Create unit tests automatically:

```python
def generate_tests(function_code: str) -> str:
    messages = [
        LanguageModelChatMessage.user(
            f"Generate pytest unit tests for this function:\n\n"
            f"{function_code}\n\n"
            f"Include edge cases and error conditions."
        )
    ]
    response = model.send_request(messages)
    return response['text']
```

### Refactoring Suggestions

Get improvement recommendations:

```python
def suggest_refactoring(code: str) -> str:
    messages = [
        LanguageModelChatMessage.user(
            f"Suggest refactoring improvements for:\n\n{code}\n\n"
            f"Focus on readability and maintainability."
        )
    ]
    response = model.send_request(messages)
    return response['text']
```

## API Reference

See the full API documentation for detailed information about:

- `LanguageModel` class and methods
- `LanguageModelChat` properties and operations  
- `LanguageModelChatMessage` message construction
- Error handling and exceptions
- Advanced options and parameters
