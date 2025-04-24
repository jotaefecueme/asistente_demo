import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

llm = init_chat_model(
    "deepseek-r1-distill-llama-70b",
    model_provider="groq"
)

st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        background-color: #FAFAFA;
    }
    .block-container {
        padding-top: 1.5rem;
    }
    h1 {
        font-size: 2.2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stChatMessage {
        max-width: 100%;
    }
    .system-prompt-container {
        margin-top: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

if "conversations" not in st.session_state:
    st.session_state.conversations = {}
    st.session_state.current_chat = None
    st.session_state.chat_titles = {}

for key, title in st.session_state.chat_titles.items():
    label = f"➡️ {title}" if key == st.session_state.current_chat else title
    if st.sidebar.button(label, key=key):
        st.session_state.current_chat = key
        st.rerun()
    
    if key == st.session_state.current_chat:
        st.write('<div class="system-prompt-container"></div>', unsafe_allow_html=True)  
        system_prompt = st.text_area(f"System prompt - {title}", 
                                     st.session_state.conversations[key][0]["content"], height=100)
        st.session_state.conversations[key][0]["content"] = system_prompt

if st.sidebar.button("➕ Nueva conversación"):
    new_id = f"Conversación {len(st.session_state.conversations) + 1}"
    st.session_state.conversations[new_id] = [{"role": "system", "content": "Eres un asistente de inteligencia artificial. Responde de forma clara, útil y sin inventar cosas.\nSi no tienes información suficiente, dilo sin problema.\n"}]
    st.session_state.chat_titles[new_id] = new_id
    st.session_state.current_chat = new_id
    st.rerun()

chat_id = st.session_state.current_chat
if chat_id is None:
    st.warning("No hay conversaciones activas.")
    st.stop()

chat_history = st.session_state.conversations[chat_id]

def render_message(role, content):
    color = "#DCF8C6" if role == "user" else "#E8E8E8"
    align = "flex-end" if role == "user" else "flex-start"
    st.markdown(
        f"""
        <div style="display: flex; justify-content: {align}; margin-bottom: 0.5rem;">
            <div style="background-color: {color}; padding: 1rem 1.2rem; border-radius: 1rem;
                        max-width: 80%; font-size: 15.5px; line-height: 1.6; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                {content}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

for msg in chat_history[1:]:  
    render_message(msg["role"], msg["content"])

user_input = st.chat_input("Escribe tu mensaje...")

if user_input:
    chat_history.append({"role": "user", "content": user_input})
    prompt = "\n".join(f"{m['role']}: {m['content']}" for m in chat_history)
    response = llm.invoke(prompt).content
    chat_history.append({"role": "assistant", "content": response})

    user_messages = [m["content"] for m in chat_history if m["role"] == "user"]
    if len(user_messages) >= 1:
        summary_prompt = (
            "Resume esta conversación en un título breve (máx. 3 palabras) que represente el tema tratado:\n\n"
            + "\n".join(user_messages)
        )
        new_title = llm.invoke(summary_prompt).content.strip().replace("\n", " ")
        st.session_state.chat_titles[chat_id] = new_title[:50]  

    st.rerun()
