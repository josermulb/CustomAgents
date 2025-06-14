# CustomAgents

This is a basic implementation of an AI agent without relying on any external framework.

The inference provider is **Ollama**, running locally on a Windows machine.
The default LLM is **Qwen3**, and the available tools are focused on operations with the operating system.

---

## Requirements

This project uses [`uv`](https://github.com/astral-sh/uv) to manage dependencies.
To install it:

```bash
pip install uv
```

---

## Try it Yourself

Run the agent via terminal with:

```bash
uv run main.py
```

---

## Project Structure

The core functionalities are organized as follows:

```
src/
├── agent.py
├── llm.py
├── tools_manager.py
└── tools/
    └── os_tools.py
```

### `agent.py`

Contains the main `Agent` class, which manages the conversation with the user and coordinates interactions with the LLM and tools.

### `llm.py`

Implements the communication layer with the LLM. It uses the Ollama API to send prompts and receive responses.

### `tools_manager.py`

Handles the dynamic loading and management of tools based on the user configuration. It acts as the bridge between the agent and the tools.

### `tools/os_tools.py`

Defines the available OS-related tools that the agent can use to interact with the operating system.
You can extend this module or add new ones to give the agent additional capabilities.