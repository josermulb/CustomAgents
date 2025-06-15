# webapp.py
import sys
import os

# --- THIS BLOCK MUST REMAIN AT THE VERY BEGINNING FOR PATH MODIFICATION ---
# Get the absolute path of the directory containing the current script (webapp.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
# In this new setup, 'current_dir' is already the project root ('CustomAgents/')
project_root = current_dir # The root is where webapp.py now resides
# Add the project root to sys.path so Python can find 'src' and 'webapp' as top-level packages
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- END OF PATH MODIFIED BLOCK ---

# >>> IMPORT STREAMLIT HERE, JUST BEFORE set_page_config <<<
import streamlit as st

# --- SET PAGE CONFIG HERE, AS THE FIRST STREAMLIT COMMAND ---
# This must be the very first Streamlit command executed in your script.
st.set_page_config(page_title="Agentic Chatbot", page_icon="💬", layout="wide")


# Now, you can import your other modules
from src.llm import Ollama
from src.agent import LLMAgent
from src.tools_manager import ToolsManager

# Import functions from your webapp modules
from webapp.sidebar import render_sidebar
from webapp.chat_page import render_chat_page


# --- Instantiate LLM and Agent ONCE with st.cache_resource ---
@st.cache_resource
def get_llm_engine():
    return Ollama()

@st.cache_resource
def get_tools_manager():
    return ToolsManager("src.tools.os_tools")

@st.cache_resource
def get_agent(_llm_engine_instance, _tools_manager_instance):
    return LLMAgent(
        llm_engine=_llm_engine_instance,
        tools_manager=_tools_manager_instance,
        model_id='qwen3',
    )

# Retrieve (or create if first run) the cached instances of LLM, ToolsManager, and Agent
llm_engine = get_llm_engine()
os_tools_manager = get_tools_manager()
os_agent = get_agent(llm_engine, os_tools_manager)


# Initialize Streamlit session state variables if they don't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_stats" not in st.session_state:
    st.session_state.agent_stats = {
        "n_calls": 0,
        "n_input_tokens": 0,
        "n_output_tokens": 0,
    }
if "current_page" not in st.session_state:
    st.session_state.current_page = "Chatbot" # Set default page


# --- Render Sidebar ---
render_sidebar(os_agent)

# --- Render Main Content Based on Current Page ---
if st.session_state.current_page == "Chatbot":
    render_chat_page(os_agent)
elif st.session_state.current_page == "Settings":
    st.header("Settings Page")
    st.write("This is the Settings page. Content coming soon!")
elif st.session_state.current_page == "Help":
    st.header("Help Page")
    st.write("This is the Help page. Content coming soon!")