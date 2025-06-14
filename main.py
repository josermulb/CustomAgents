from src.llm import Ollama
from src.agent import LLMAgent
from src.tools_manager import ToolsManager

def main():
    llm_engine = Ollama()
    os_tools_manager = ToolsManager("src.tools.os_tools")
    os_agent = LLMAgent(
        llm_engine=llm_engine,
        tools_manager=os_tools_manager,
        model_id = 'qwen3',
    )

    print("Hello, you can interact here with the AI Agent.")
    print("To stop chatting, type 'stop'")

    input_string = ""
    while input_string != 'stop':
        input_string = input('Type your requirement now: ')
        chat_history = os_agent.run(prompt=input_string)
        print(chat_history[-1]['content'])

if __name__ == "__main__":
    main()