from ollama import chat
from abc import ABC, abstractmethod


class LlmEngine(ABC):
    """
    Abstract Base Class (ABC) for Language Model (LLM) engines.

    This class defines the interface that all concrete LLM engine implementations
    must adhere to, ensuring a consistent way to interact with different LLMs.
    """

    @abstractmethod
    def chat(
        self,  # Added 'self' for instance method
        model_id: str,
        messages: list,
        model_params: dict = {},
        tools: list[dict] = {},
    ):
        """
        Abstract method to interact with a Language Model in a conversational manner.

        Concrete implementations must provide the logic for sending messages to
        a specific LLM and receiving its response.

        Args:
            model_id (str): The identifier of the LLM model to use (e.g., 'llama3', 'gpt-4o').
            messages (list): A list of message dictionaries representing the conversation history.
                             Each dictionary should follow the format {"role": "...", "content": "..."}.
            model_params (dict, optional): A dictionary of model-specific parameters (e.g., temperature, top_p).
                                          Defaults to an empty dictionary.
            tools (list[dict], optional): A list of tool schemas (functions) that the LLM can use.
                                         Defaults to an empty list.

        Returns:
            tuple: A tuple containing:
                   - The raw response object from the LLM API.
                   - The updated list of messages, including the LLM's response.
        """
        pass


class Ollama(LlmEngine):
    """
    A concrete implementation of LlmEngine for interacting with Ollama models.

    This class provides the specific logic to call the Ollama `chat` function,
    pass conversation messages, model parameters, and tools, and process the response.
    """

    def __init__(self):
        """
        Initializes the Ollama engine.

        Currently, this constructor does not require any parameters as the Ollama
        client typically manages its own connection to the local server.
        """
        pass

    def chat(
            self,
            model_id: str,
            messages: list,
            model_params: dict = {},
            tools: list[dict] = {},
            think: bool = True,
            ):
        """
        Interacts with an Ollama model in a conversational manner.

        Sends the given messages, model parameters, and available tools to the
        specified Ollama model and appends the model's response to the messages list.

        Args:
            model_id (str): The identifier of the Ollama model to use (e.g., 'llama3', 'qwen3').
            messages (list): A list of message dictionaries representing the conversation history.
                             Each dictionary should follow the format {"role": "...", "content": "..."}.
            model_params (dict, optional): A dictionary of Ollama-specific options (e.g., 'temperature', 'num_ctx').
                                          Defaults to an empty dictionary.
            tools (list[dict], optional): A list of tool schemas (functions) that the Ollama model can use.
                                         Defaults to an empty list.
            think (bool, optional): A specific Ollama parameter to enable thinking in tool calls.
                                    Defaults to True.

        Returns:
            tuple: A tuple containing:
                   - The raw response object from the Ollama API call.
                   - The updated list of messages, with the Ollama model's response appended.
        """

        response = chat(
            model=model_id,
            messages=messages,
            tools=tools,
            options=model_params,
            think=think
        )
        if response.message:
            # `response.message.model_dump()` converts the Pydantic model response
            # into a dictionary suitable for appending to the messages list.
            messages.append(response.message.model_dump())
        
        return response, messages