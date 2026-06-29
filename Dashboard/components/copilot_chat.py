import streamlit as st
from services.api_client import ask_copilot
    
def render_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello NOC Operator. I am your AI Copilot. How can I assist you with the network today?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about network health, predictions, or troubleshooting..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_copilot(prompt)  # {answer, sources}
                answer = response.get("answer", "No answer returned.")
                sources = response.get("sources", [])
                st.markdown(answer)
                if sources:
                    st.caption("Sources: " + ", ".join(sources))
        st.session_state.messages.append({"role": "assistant", "content": answer})
