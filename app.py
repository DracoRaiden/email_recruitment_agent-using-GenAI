import streamlit as st
from agent_backend import app as agent_app

st.set_page_config(page_title="GIKI Recruitment Agent", layout="wide")

st.title("🤖 GIKI HR Assistant")

# --- 1. SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I am the GIKI Recruitment Assistant. How can I help you today?"}
    ]

if "agent_state" not in st.session_state:
    # Initialize the memory of the agent
    st.session_state.agent_state = {
        "chat_history": [],
        "logs": [],
        "user_id": None,
        "recipient_email": None,
        "status": None,
        "awaiting_email_confirmation": False,
        "email_sent": False
    }

# --- 2. LAYOUT ---
# Chat on left, Debug on right
chat_col, debug_col = st.columns([2, 1])

# --- 3. RENDER DEBUG PANEL (Right Column) ---
with debug_col:
    st.subheader("🕵️ Internal Agent State")
    st.caption("Live monitoring of agent memory and decisions.")
    
    with st.container(border=True):
        st.write("**Extracted Info:**")
        st.write(f"🆔 User ID: `{st.session_state.agent_state['user_id']}`")
        st.write(f"📧 Email: `{st.session_state.agent_state['recipient_email']}`")
        st.write(f"📊 Status: `{st.session_state.agent_state['status']}`")
        st.write(f"⏳ Waiting Confirm: `{st.session_state.agent_state['awaiting_email_confirmation']}`")
        
    with st.expander("📜 System Logs", expanded=True):
        if st.session_state.agent_state.get('logs'):
            for log in st.session_state.agent_state['logs']:
                st.code(log, language="text")
        else:
            st.write("No logs yet.")

# --- 4. RENDER CHAT (Left Column) ---
with chat_col:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input("Type your message here..."):
        # 1. Add user message to UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Prepare inputs for the Backend
        current_state = st.session_state.agent_state
        current_state["last_user_message"] = prompt
        
        # 3. RUN THE AGENT
        with st.spinner("Agent is thinking..."):
            try:
                # Run graph (invoke returns the final state)
                result_state = agent_app.invoke(current_state)
                
                # 4. Update Session State
                st.session_state.agent_state = result_state
                bot_response = result_state.get("final_response", "I'm not sure what to say.")
                
                # 5. Display Bot Response
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
                with st.chat_message("assistant"):
                    st.markdown(bot_response)
                    
                # Force rerun to update debug panel instantly
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")