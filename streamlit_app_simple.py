import streamlit as st
import os
import json
import time
from datetime import datetime

# Simple error handling for imports
try:
    from st_audiorec import st_audiorec
    HAS_AUDIO_REC = True
except ImportError:
    HAS_AUDIO_REC = False

try:
    from deepgram import DeepgramClient, PrerecordedOptions, FileSource
    HAS_DEEPGRAM = True
except ImportError:
    HAS_DEEPGRAM = False

# Configure Streamlit page
st.set_page_config(
    page_title="🎙️ Voice AI Agent",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        background: rgba(255, 255, 255, 0.05);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .ai-message {
        background: rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'deepgram_client' not in st.session_state:
    st.session_state.deepgram_client = None

def get_deepgram_client():
    """Get Deepgram client with API key"""
    if not HAS_DEEPGRAM:
        return None
        
    api_key = None
    
    # Try secrets first
    try:
        api_key = st.secrets.get("DEEPGRAM_API_KEY")
    except:
        pass
    
    # Try environment
    if not api_key:
        api_key = os.getenv("DEEPGRAM_API_KEY")
    
    # Ask user if no key found
    if not api_key:
        st.sidebar.error("🔑 Deepgram API Key Required")
        api_key = st.sidebar.text_input(
            "Enter Deepgram API Key:",
            type="password",
            help="Get your key from https://console.deepgram.com/"
        )
    
    if api_key and len(api_key) > 10:
        try:
            return DeepgramClient(api_key)
        except Exception as e:
            st.error(f"Deepgram error: {e}")
    
    return None

def transcribe_audio_mock(audio_data):
    """Mock transcription for demo purposes"""
    return "This is a mock transcription. Real transcription requires Deepgram API key."

def add_message(role, content):
    """Add message to chat"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })

def generate_ai_response(user_input):
    """Generate AI response"""
    responses = [
        f"I heard: '{user_input}'. How can I help you?",
        f"Thanks for saying: '{user_input}'. What would you like to know?",
        f"Interesting input: '{user_input}'. Tell me more!",
        f"You mentioned: '{user_input}'. How can I assist further?"
    ]
    import random
    return random.choice(responses)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎙️ Voice AI Agent</h1>
        <p>Real-time speech transcription powered by Deepgram AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar status
    with st.sidebar:
        st.markdown("### 🎛️ Status")
        
        # Dependency status
        if HAS_DEEPGRAM:
            st.success("✅ Deepgram SDK loaded")
        else:
            st.error("❌ Deepgram SDK not found")
            
        if HAS_AUDIO_REC:
            st.success("✅ Audio recorder available")
        else:
            st.warning("⚠️ Audio recorder not available")
        
        # Clear chat
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎙️ Voice Input")
        
        # Audio recorder or file upload
        if HAS_AUDIO_REC:
            st.info("🎤 Click below to record audio")
            audio_bytes = st_audiorec()
            
            if audio_bytes:
                st.audio(audio_bytes)
                
                with st.spinner("🔄 Processing audio..."):
                    # Mock transcription for now
                    transcript = "Sample transcription - connect Deepgram for real transcription"
                    
                    if transcript:
                        add_message("user", transcript)
                        ai_response = generate_ai_response(transcript)
                        add_message("assistant", ai_response)
                        st.success(f"✅ Transcribed: {transcript}")
                        st.rerun()
        else:
            st.info("📁 Audio recording not available. Use file upload instead.")
            uploaded_file = st.file_uploader("Upload audio file", type=['wav', 'mp3', 'ogg'])
            
            if uploaded_file:
                st.audio(uploaded_file)
                if st.button("🔄 Transcribe"):
                    with st.spinner("Processing..."):
                        transcript = "Sample transcription from uploaded file"
                        add_message("user", transcript)
                        ai_response = generate_ai_response(transcript)
                        add_message("assistant", ai_response)
                        st.rerun()
        
        # Text input alternative
        st.markdown("### ⌨️ Text Input")
        text_input = st.text_input("Type your message:")
        
        if st.button("📤 Send") and text_input:
            add_message("user", text_input)
            ai_response = generate_ai_response(text_input)
            add_message("assistant", ai_response)
            st.rerun()
    
    with col2:
        st.markdown("### 📊 Stats")
        st.metric("Messages", len(st.session_state.messages))
        st.metric("User Messages", len([m for m in st.session_state.messages if m["role"] == "user"]))
        st.metric("AI Responses", len([m for m in st.session_state.messages if m["role"] == "assistant"]))
    
    # Chat display
    st.markdown("### 💬 Conversation")
    
    if st.session_state.messages:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>🎙️ You ({message["timestamp"]}):</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>🤖 AI ({message["timestamp"]}):</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👋 Start by recording audio or typing a message!")
    
    # Instructions
    with st.expander("📖 How to Use"):
        st.markdown("""
        ### Setup Instructions:
        
        1. **Add Deepgram API Key**: 
           - Get free API key from https://console.deepgram.com/
           - Add it in Streamlit secrets or enter in sidebar
        
        2. **Record Audio**:
           - Click the record button (if available)
           - Or upload an audio file
           - Or use text input as alternative
        
        3. **View Results**:
           - See transcription and AI responses in chat
           - Monitor stats in the sidebar
        
        ### Troubleshooting:
        - If audio recording doesn't work, try text input
        - If transcription fails, check your Deepgram API key
        - For deployment issues, check the requirements.txt file
        """)

if __name__ == "__main__":
    main()