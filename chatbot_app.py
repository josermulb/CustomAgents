import streamlit as st
import logging
import threading
import queue
import time
from src.llm import Ollama
from src.agent import LLMAgent
from src.tools_manager import ToolsManager

class QueueLoggerHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        log_entry = self.format(record)
        self.log_queue.put(log_entry)


# Page configuration for a wide layout
st.set_page_config(page_title="Chatbot", page_icon="💬", layout="wide")

# --- Instantiate LLM and Agent ONCE with st.cache_resource ---
# st.cache_resource caches the object in memory and reuses it on reruns.
# This ensures that n_calls, n_input_tokens, etc., do not reset.

@st.cache_resource
def get_llm_engine():
    return Ollama()

@st.cache_resource
def get_tools_manager():
    # Ensure that ToolsManager can be cached,
    # i.e., it has no dependencies that change with each rerun
    return ToolsManager("src.tools.os_tools")

@st.cache_resource
def get_agent(_llm_engine_instance, _tools_manager_instance):
    # Arguments that cannot be hashed have a leading underscore.
    return LLMAgent(
        llm_engine=_llm_engine_instance,
        tools_manager=_tools_manager_instance,
        model_id='qwen3',
    )

llm_engine = get_llm_engine()
os_tools_manager = get_tools_manager()
os_agent = get_agent(llm_engine, os_tools_manager)


# Initialize session_state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_stats" not in st.session_state:
    st.session_state.agent_stats = {
        "n_calls": 0,
        "n_input_tokens": 0,
        "n_output_tokens": 0,
    }

# --- COMPLETE LEFT SIDEBAR ---
with st.sidebar:
    st.image("https://via.placeholder.com/150", caption="Logo (Placeholder)") # You can put your logo here
    st.title("Navigation")
    st.write("---") # Visual separator

    # Placeholders for pages
    if st.button("💬 Chatbot (Current)"):
        st.session_state.current_page = "Chatbot" # This is just an example of how you could handle it
    if st.button("⚙️ Settings (Coming Soon)"):
        st.session_state.current_page = "Settings"
        st.info("Settings page is under construction!")
    if st.button("❓ Help (Coming Soon)"):
        st.session_state.current_page = "Help"
        st.info("Help page is under construction!")

    # Spacer to push stats to the bottom
    # Adjust height as needed (e.g., "30vh", "300px", etc.)
    st.markdown("<div style='height: 30vh;'></div>", unsafe_allow_html=True)

    # Placeholder for agent stats at the bottom of the sidebar
    agent_stats_sidebar_placeholder = st.empty()

    # Footer information for the sidebar
    st.markdown("---")
    st.markdown("Developed by José Ángel Rodríguez Murillo")


# Function to update stats in the sidebar
def update_agent_stats_panel_sidebar(calls, input_tokens, output_tokens):
    with agent_stats_sidebar_placeholder:
        st.markdown(f"""
            <div style="
                background-color:#202020;
                padding: 10px;
                border-radius: 5px;
                color: white;
            ">
                <h3 style="margin-top: 0; color: #ADD8E6;">🧠 Agent Stats</h3>
                <ul style="list-style-type: none; padding: 0;">
                    <li style="margin-bottom: 5px;"><strong>Calls</strong>: <span style="font-weight: bold; color: #90EE90;">{calls}</span></li>
                    <li style="margin-bottom: 5px;"><strong>Input tokens</strong>: <span style="font-weight: bold; color: #FFD700;">{input_tokens / 1000:.2f}k</span></li>
                    <li style="margin-bottom: 5px;"><strong>Output tokens</strong>: <span style="font-weight: bold; color: #FFA07A;">{output_tokens / 1000:.2f}k</span></li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

# Call the stats update function at the start so the panel
# is displayed with initial values (0, 0, 0) in the sidebar.
update_agent_stats_panel_sidebar(
    os_agent.n_calls,
    os_agent.n_input_tokens,
    os_agent.n_output_tokens
)


# --- MAIN CONTENT (The Chat) ---
st.title("💬 Chatbot")

# Display existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Type your message...")

# When the user sends a message
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # Placeholders for logs and bot response within the chat
        log_placeholder = st.empty()
        response_placeholder = st.empty()

        # Logger setup
        log_queue = queue.Queue()
        backend_logger = logging.getLogger("src")
        handler = QueueLoggerHandler(log_queue)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        if handler not in backend_logger.handlers:
            backend_logger.addHandler(handler)
        backend_logger.setLevel(logging.INFO)

        result_container = {}

        # Function to run the agent in a separate thread
        def run_agent():
            try:
                result_container["chat_history"] = os_agent.run(prompt=user_input)
            except Exception as e:
                result_container["error"] = str(e)

        thread = threading.Thread(target=run_agent)
        thread.start()

        logs_accumulated = ""

        # Update loop while the agent is active or logs are in the queue
        while thread.is_alive() or not log_queue.empty():
            # Update logs
            try:
                while True:
                    log_line = log_queue.get_nowait()
                    logs_accumulated += log_line + "\n"
            except queue.Empty:
                pass
            log_placeholder.markdown(f"```text\n{logs_accumulated.strip()}\n```")

            # Update agent metrics in the sidebar
            update_agent_stats_panel_sidebar(
                os_agent.n_calls,
                os_agent.n_input_tokens,
                os_agent.n_output_tokens
            )
            time.sleep(0.2) # Small pause to avoid overwhelming the UI

        thread.join() # Wait for the agent thread to finish
        backend_logger.removeHandler(handler) # Clean up the logger handler

        # Display the final bot response
        if "chat_history" in result_container:
            bot_reply = result_container["chat_history"][-1]['content']
            response_placeholder.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        else:
            response_placeholder.error("An error occurred: " + result_container.get("error", "Unknown error"))

    # Ensure the final agent stats are updated in the sidebar
    update_agent_stats_panel_sidebar(
        os_agent.n_calls,
        os_agent.n_input_tokens,
        os_agent.n_output_tokens
    )
    st.rerun() # Rerender the app to ensure everything updates visually.