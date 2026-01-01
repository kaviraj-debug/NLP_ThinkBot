import streamlit as st
import time
import os
import uuid
from chatbot import ChatbotEngine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ThinkBot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a Premium Dark Theme
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Sidebar Headers */
    .sidebar-header {
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #58a6ff;
        border-bottom: 1px solid #30363d;
        padding-bottom: 0.3rem;
    }
    
    /* Buttons in Sidebar */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
        transition: all 0.3s ease;
        text-align: left;
    }
    
    .stButton>button:hover {
        background-color: #30363d;
        border-color: #8b949e;
        color: #ffffff;
    }

    /* Chat Message Bubbles */
    .stChatMessage {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    
    /* Highlight active chat in sidebar */
    .active-chat {
        background-color: #1f6feb !important;
        border-radius: 8px;
        padding: 8px 12px;
        color: white;
        font-size: 0.9rem;
        margin-bottom: 5px;
        border: 1px solid #58a6ff;
    }
    
    /* User Message Specific Highlight */
    div[data-testid="stChatMessageUser"] {
        background-color: #0d1117;
        border-right: 4px solid #1f6feb;
    }
    
    /* Bot Message Specific Highlight */
    div[data-testid="stChatMessageAssistant"] {
        border-left: 4px solid #238636;
    }
    
    /* Input Box */
    .stChatInputContainer {
        border-top: 1px solid #30363d;
        background-color: #0d1117;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
""", unsafe_allow_html=True)

# Constants
INITIAL_GREETING = "Hi!\nHow can I help You Today?"

# Initialize session state
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

if "chats" not in st.session_state:
    # Initialize with one empty chat
    chat_id = str(uuid.uuid4())
    st.session_state.chats = {
        chat_id: {
            "title": "New Chat",
            "messages": [{"role": "assistant", "content": INITIAL_GREETING}],
            "created_at": time.time()
        }
    }
    st.session_state.current_chat_id = chat_id

# Initialize chatbot engine
@st.cache_resource
def get_bot(api_key):
    try:
        if not api_key:
            return None
        return ChatbotEngine(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize AI: {str(e)}")
        return None

# Sidebar Content
with st.sidebar:
    # 1. New Chat Button at the very top
    if st.button("➕ New Chat", use_container_width=True, help="Start a fresh conversation"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {
            "title": "New Chat",
            "messages": [{"role": "assistant", "content": INITIAL_GREETING}],
            "created_at": time.time()
        }
        st.session_state.current_chat_id = new_id
        st.rerun()
    
    st.divider()
    
    # 2. Your Chats Section - Hidden if no messages yet
    st.markdown('<div class="sidebar-header">🧠 Your Chats</div>', unsafe_allow_html=True)
    
    # List chats in reverse chronological order
    sorted_chat_ids = sorted(st.session_state.chats.keys(), 
                             key=lambda k: st.session_state.chats[k]["created_at"], 
                             reverse=True)
    
    # Only show chats that have at least one user message (or modified title)
    visible_chats = [cid for cid in sorted_chat_ids if st.session_state.chats[cid]["title"] != "New Chat" or len(st.session_state.chats[cid]["messages"]) > 1]
    
    if not visible_chats:
        st.info("Your chat list is empty. Start typing to save a conversation!")
    else:
        for c_id in visible_chats:
            chat = st.session_state.chats[c_id]
            is_active = (c_id == st.session_state.current_chat_id)
            
            if is_active:
                st.markdown(f'<div class="active-chat">✨ {chat["title"]}</div>', unsafe_allow_html=True)
            else:
                if st.button(f"💬 {chat['title']}", key=f"nav_{c_id}", use_container_width=True):
                    st.session_state.current_chat_id = c_id
                    st.rerun()

    st.divider()
    
    st.markdown('<div class="sidebar-header">🛠️ Options</div>', unsafe_allow_html=True)
    response_speed = st.select_slider(
        "Response Speed",
        options=["Fast", "Natural", "Detailed"],
        value="Natural"
    )
    
    if st.button("🗑️ Reset Current Chat", use_container_width=True):
        st.session_state.chats[st.session_state.current_chat_id] = {
            "title": "New Chat",
            "messages": [{"role": "assistant", "content": INITIAL_GREETING}],
            "created_at": time.time()
        }
        st.rerun()

# Main UI Header
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>🧠🤖 ThinkBot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>“Built to think with you.”</p>", unsafe_allow_html=True)
st.markdown("---")

bot = get_bot(st.session_state.api_key)

# Access current chat session
current_chat = st.session_state.chats[st.session_state.current_chat_id]

# Display messages
for msg in current_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input handling
if prompt := st.chat_input("Hello I am ThinkBot"):
    # Add user message
    with st.chat_message("user"):
        st.markdown(prompt)
    current_chat["messages"].append({"role": "user", "content": prompt})
    
    # Auto-update summary title if it's the first message
    if current_chat["title"] == "New Chat":
        current_chat["title"] = prompt[:35] + ("..." if len(prompt) > 35 else "")

    # Assistant Response
    if bot:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            with st.spinner("ThinkBot is thinking..."):
                # Prepare context for Gemini
                api_history = []
                # First message is greeting, Gemini usually starts with User.
                # We skip the initial greeting if it's just the 'Hi!' message from bot.
                # Actually, Gemini 1.5/pro chat starts with an empty history or User.
                # We'll map 'assistant' to 'model' and 'user' to 'user'.
                for m in current_chat["messages"][:-1]:
                    # Skip the system greeting to avoid model errors if it expects user first
                    if m["content"] == INITIAL_GREETING: continue
                    api_history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})
                
                response_text = bot.get_response(prompt, chat_history=api_history)
                
                # Check for quota errors
                if "429" in response_text or "quota" in response_text.lower():
                    st.error("📈 Quota limit reached. Please wait a minute or try again later.")
                
                # Typing effect
                words = response_text.split(" ")
                delay = 0.02
                if response_speed == "Fast": delay = 0.005
                elif response_speed == "Detailed": delay = 0.05
                
                for i, word in enumerate(words):
                    full_response += word + (" " if i < len(words)-1 else "")
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(delay)
                
                message_placeholder.markdown(full_response)
        
        current_chat["messages"].append({"role": "assistant", "content": full_response})
        st.rerun() # Ensure the sidebar update is visible immediately
    else:
        st.error("Ensure your API Key is set in the .env file.")
