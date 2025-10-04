"""
Language Model API for VS Code Sockpuppet.

This module provides access to VS Code's Language Model API, enabling Python
scripts to interact with Copilot and other language models directly.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .client import VSCodeClient


class LanguageModelChatMessage:
    """Represents a chat message for language model requests."""

    def __init__(self, role: str, content: str):
        """
        Create a chat message.

        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        self.role = role
        self.content = content

    @classmethod
    def user(cls, content: str) -> "LanguageModelChatMessage":
        """
        Create a user message.

        Args:
            content: The user's message content

        Returns:
            A chat message with role 'user'

        Example:
            msg = LanguageModelChatMessage.user("Explain this code")
        """
        return cls("user", content)

    @classmethod
    def assistant(cls, content: str) -> "LanguageModelChatMessage":
        """
        Create an assistant message.

        Args:
            content: The assistant's message content

        Returns:
            A chat message with role 'assistant'

        Example:
            msg = LanguageModelChatMessage.assistant("This code...")
        """
        return cls("assistant", content)

    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary for JSON serialization."""
        return {"role": self.role, "content": self.content}


class LanguageModelChat:
    """Represents a language model for making chat requests."""

    def __init__(self, client: "VSCodeClient", model_data: Dict[str, Any]):
        """
        Initialize a language model.

        Args:
            client: VSCode client instance
            model_data: Model metadata from VS Code
        """
        self.client = client
        self._id = model_data["id"]
        self._name = model_data["name"]
        self._vendor = model_data["vendor"]
        self._family = model_data["family"]
        self._version = model_data["version"]
        self._max_input_tokens = model_data["maxInputTokens"]

    @property
    def id(self) -> str:
        """Unique identifier of the language model."""
        return self._id

    @property
    def name(self) -> str:
        """Human-readable name of the model."""
        return self._name

    @property
    def vendor(self) -> str:
        """Vendor of the model (e.g., 'copilot')."""
        return self._vendor

    @property
    def family(self) -> str:
        """Model family (e.g., 'gpt-4o', 'gpt-3.5-turbo')."""
        return self._family

    @property
    def version(self) -> str:
        """Model version."""
        return self._version

    @property
    def max_input_tokens(self) -> int:
        """Maximum number of input tokens the model supports."""
        return self._max_input_tokens

    def send_request(
        self,
        messages: List[LanguageModelChatMessage],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a chat request to the language model.

        Args:
            messages: List of chat messages
            options: Optional request options (e.g., temperature, top_p)

        Returns:
            Response dictionary with 'text' (full response) and
            'parts' (individual fragments)

        Raises:
            Exception: If the model is not available or request fails

        Example:
            messages = [
                LanguageModelChatMessage.user("Explain async/await")
            ]
            response = model.send_request(messages)
            print(response['text'])
        """
        message_dicts = [msg.to_dict() for msg in messages]
        return self.client._send_request(
            "lm.sendRequest",
            {
                "modelId": self._id,
                "messages": message_dicts,
                "options": options or {},
            },
        )

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.

        Args:
            text: The text to count tokens for

        Returns:
            Number of tokens

        Example:
            tokens = model.count_tokens("Hello, world!")
            print(f"Token count: {tokens}")
        """
        return self.client._send_request("lm.countTokens", {"modelId": self._id, "text": text})

    def __repr__(self) -> str:
        """String representation of the model."""
        return (
            f"LanguageModelChat(id={self._id!r}, vendor={self._vendor!r}, family={self._family!r})"
        )


class LanguageModel:
    """
    Language Model API for interacting with Copilot and other LLMs.

    This class provides access to VS Code's Language Model API, allowing
    Python scripts to select and interact with available language models.
    """

    def __init__(self, client: "VSCodeClient"):
        """
        Initialize the language model API.

        Args:
            client: VSCode client instance
        """
        self.client = client

    def select_chat_models(
        self,
        vendor: Optional[str] = None,
        family: Optional[str] = None,
        version: Optional[str] = None,
        id: Optional[str] = None,
    ) -> List[LanguageModelChat]:
        """
        Select language models matching the given criteria.

        Args:
            vendor: Filter by vendor (e.g., 'copilot')
            family: Filter by model family (e.g., 'gpt-4o')
            version: Filter by version
            id: Filter by specific model ID

        Returns:
            List of matching language models

        Raises:
            Exception: If no models match the criteria or models not available

        Example:
            # Get all Copilot models
            models = client.lm.select_chat_models(vendor='copilot')

            # Get specific model family
            models = client.lm.select_chat_models(
                vendor='copilot',
                family='gpt-4o'
            )

            # Get specific model by ID
            models = client.lm.select_chat_models(
                id='copilot-gpt-4o'
            )
        """
        selector = {}
        if vendor is not None:
            selector["vendor"] = vendor
        if family is not None:
            selector["family"] = family
        if version is not None:
            selector["version"] = version
        if id is not None:
            selector["id"] = id

        models_data = self.client._send_request("lm.selectChatModels", {"selector": selector})
        return [LanguageModelChat(self.client, model_data) for model_data in models_data]
