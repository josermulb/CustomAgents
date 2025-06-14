import logging
from src.llm import LlmEngine
from src.tools_manager import ToolsManager


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

class LLMAgent:
    """
    Represents a Large Language Model (LLM) agent capable of interacting with users,
    utilizing tools, and maintaining a conversation history.

    This agent encapsulates the logic for making calls to an LLM,
    processing responses (including executing tool calls), and
    tracking metrics related to token usage and execution times.
    """

    def __init__(
            self,
            llm_engine: LlmEngine,
            tools_manager: ToolsManager,
            system_prompt: str = '',
            model_id: str = 'qwen3',
            model_params: dict = {},
            ):
        """
        Initializes a new LLMAgent instance.

        Args:
            llm_engine (LlmEngine): An instance of the LLM engine to make model calls.
            tools_manager (ToolsManager): An instance of the tool manager to execute functions.
            system_prompt (str, optional): The initial system prompt for the model.
                                            This is added to the message history at the start. Defaults to ''.
            model_id (str, optional): The identifier of the LLM model to use (e.g., 'qwen3', 'llama3').
                                      Defaults to 'qwen3'.
            model_params (dict, optional): A dictionary of additional parameters for the model (e.g., temperature, top_p).
                                          Defaults to {}.
        """
        self.llm_engine = llm_engine
        self.tools_manager = tools_manager

        self.system_prompt = system_prompt
        self.model_id = model_id
        self.model_params = model_params

        self.clear_conversation()

    def clear_conversation(self):
        """
        Resets the agent's conversation history and all usage metrics.

        This method resets the counters for LLM calls, input/output tokens, and execution times.
        If a `system_prompt` was defined during agent initialization, it is re-added
        to the message history.
        """
        self.n_calls = 0
        self.n_input_tokens = 0
        self.input_time = 0
        self.n_output_tokens = 0
        self.output_time = 0

        if self.system_prompt:
            self.messages = [{
                "role": "system",
                "content": self.system_prompt
            }]
        else:
            self.messages = []

    def update_metrics(self, response) -> None:
        """
        Updates the agent's usage metrics based on an LLM response.

        Aggregates input and output token counts, as well as evaluation durations,
        to the agent's internal counters.

        Args:
            response: The response object returned by the LLM engine, which should contain
                      `prompt_eval_count`, `eval_count`, `prompt_eval_duration`, and `eval_duration`.
        """
        self.n_input_tokens += response.prompt_eval_count
        self.n_output_tokens += response.eval_count
        self.input_time += response.prompt_eval_duration
        self.output_time += response.eval_duration

    def run(
            self,
            prompt: str,
            ) -> list[dict]:
        """
        Executes the agent with a new user prompt, handling LLM interactions
        and tool calls.

        This method appends the user's prompt to the history, makes one or more
        calls to the LLM, executes tools if requested by the model, and updates metrics.
        The cycle continues until the LLM generates a final response without tool calls.

        Args:
            prompt (str): The user's input message.

        Returns:
            list[dict]: The complete message history of the conversation, including
                        the user's prompt, assistant responses, and tool results.
        """
        self.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        self.n_calls += 1
        logger.info(f"Doing LLM call number {self.n_calls}")

        response, self.messages = self.llm_engine.chat(
            model_id=self.model_id,
            messages=self.messages,
            tools=self.tools_manager.tools,
            model_params=self.model_params
        )
        self.update_metrics(response)

        while response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                logger.info(f"Executing tool {tool_call.function.name} with the parameters: {tool_call.function.arguments}")
                self.messages.append(
                    {
                        'role': 'tool',
                        'tool_call_id': tool_call.function.name,
                        'content': str(self.tools_manager.call_function(tool_call.function.name, tool_call.function.arguments))
                    }
                )
            self.n_calls += 1
            logger.info(f"Doing LLM call number {self.n_calls}")
            response, self.messages = self.llm_engine.chat(
                model_id=self.model_id,
                messages=self.messages,
                tools=self.tools_manager.tools,
                model_params=self.model_params
            )
            self.update_metrics(response)
        return self.messages