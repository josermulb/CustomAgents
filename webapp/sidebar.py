# webapp/sidebar.py
import streamlit as st
import logging
import queue

# Initialize a global variable to hold the placeholder, but don't create it with st.empty() here.
_agent_stats_sidebar_placeholder = None

def update_agent_stats_panel_sidebar(calls, input_tokens, output_tokens):
    """
    Updates the agent stats panel in the sidebar.
    This function is called by render_sidebar initially and by chat_page during agent execution.
    """
    global _agent_stats_sidebar_placeholder
    if _agent_stats_sidebar_placeholder is not None:
        # ALL Streamlit calls that should be in the sidebar must be within 'with st.sidebar:'
        # However, since _agent_stats_sidebar_placeholder is already created within the sidebar context
        # in render_sidebar, just using it directly here is fine.
        with _agent_stats_sidebar_placeholder:
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
    else:
        logging.warning("Sidebar placeholder not initialized. Call render_sidebar first.")


def render_sidebar(os_agent):
    """
    Renders the complete left sidebar including navigation and agent stats.
    """
    global _agent_stats_sidebar_placeholder
    with st.sidebar: # <--- Crucial: Ensure all sidebar content is here
        
        _, col2, _ = st.columns([1, 6, 1])
        with col2:
            st.image(
                "data\images\logo.jpg",
                use_container_width =True
                )
            st.title("Navigation")
            st.write("---") # Visual separator

            # Navigation buttons with placeholders for future pages
            if st.button("💬 Chatbot"):
                st.session_state.current_page = "Chatbot"
            if st.button("⚙️ Settings (Coming Soon)"):
                st.session_state.current_page = "Settings"
                st.info("Settings page is under construction!")
            if st.button("❓ Help (Coming Soon)"):
                st.session_state.current_page = "Help"
                st.info("Help page is under construction!")

        # Spacer div to push the agent stats to the bottom of the sidebar
        st.markdown("<div style='height: 30vh;'></div>", unsafe_allow_html=True)

        # Create the placeholder within the st.sidebar context
        _agent_stats_sidebar_placeholder = st.empty()

        # Footer information for the sidebar
        st.markdown("---")
        st.markdown("Developed by JARM")

    # Initial call to update stats when the app loads or reruns.
    # This call is outside `with st.sidebar:` but it updates a placeholder
    # that was created INSIDE `with st.sidebar:`, which is the correct pattern.
    update_agent_stats_panel_sidebar(
        os_agent.n_calls,
        os_agent.n_input_tokens,
        os_agent.n_output_tokens
    )