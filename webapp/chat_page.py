# webapp/chat_page.py
import streamlit as st
import logging
import threading
import queue
import time
# Import the sidebar update function to update stats during chat interaction
from webapp.sidebar import update_agent_stats_panel_sidebar

# Custom logging handler to capture agent logs and display them in the UI
class QueueLoggerHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        log_entry = self.format(record)
        self.log_queue.put(log_entry)

def render_chat_page(os_agent):
    """
    Renders the main chat interface and handles user interaction with the agent.
    """
    st.title("💬 Chatbot")

    # Display existing messages from session state
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input chat box
    user_input = st.chat_input("Type your message...")

    # Process user input when a message is sent
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            # Placeholders for displaying logs and the final bot response
            log_placeholder = st.empty()
            response_placeholder = st.empty()

            # Configure logger to capture output from the agent's execution
            log_queue = queue.Queue()
            backend_logger = logging.getLogger("src") # Logger for your src modules
            handler = QueueLoggerHandler(log_queue)
            handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            
            # Ensure the handler is added only once to prevent duplicate log entries on rerun
            if handler not in backend_logger.handlers:
                backend_logger.addHandler(handler)
            backend_logger.setLevel(logging.INFO) # Set appropriate logging level

            result_container = {} # Container to hold the result from the agent thread

            # Function to run the agent in a separate thread to prevent UI freezing
            def run_agent_thread():
                try:
                    # Execute the agent with the user's prompt
                    result_container["chat_history"] = os_agent.run(prompt=user_input)
                except Exception as e:
                    # Capture any errors during agent execution
                    result_container["error"] = str(e)

            # Start the agent execution in a new thread
            thread = threading.Thread(target=run_agent_thread)
            thread.start()

            logs_accumulated = ""

            # Loop to continuously update UI with logs and agent stats while the agent is running
            while thread.is_alive() or not log_queue.empty():
                # Read and accumulate logs from the queue
                try:
                    while True:
                        log_line = log_queue.get_nowait()
                        logs_accumulated += log_line + "\n"
                except queue.Empty:
                    pass # No new logs yet

                # Display accumulated logs in the dedicated placeholder
                log_placeholder.markdown(f"```text\n{logs_accumulated.strip()}\n```")

                # Update agent metrics in the sidebar in real-time
                update_agent_stats_panel_sidebar(
                    os_agent.n_calls,
                    os_agent.n_input_tokens,
                    os_agent.n_output_tokens
                )
                time.sleep(0.2) # Short delay to prevent excessive UI updates

            thread.join() # Wait for the agent thread to complete its execution
            backend_logger.removeHandler(handler) # Remove the logger handler to clean up

            # Display the final response from the bot or an error message
            if "chat_history" in result_container:
                bot_reply = result_container["chat_history"][-1]['content']
                response_placeholder.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            else:
                response_placeholder.error("An error occurred: " + result_container.get("error", "Unknown error"))

        # Final update of agent stats in the sidebar after the interaction
        update_agent_stats_panel_sidebar(
            os_agent.n_calls,
            os_agent.n_input_tokens,
            os_agent.n_output_tokens
        )
        st.rerun() # Trigger a rerun to clear the input box and update the UI