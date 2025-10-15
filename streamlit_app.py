import streamlit as st
import os
import json
import base64
from io import BytesIO
import tempfile
import time
from datetime import datetime

# Try importing audio recorder
try:
    from audiorecorder import audiorecorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False

# Try importing Deepgram
try:
    from deepgram import DeepgramClient, PrerecordedOptions, FileSource
    DEEPGRAM_AVAILABLE = True
except ImportError:
    DEEPGRAM_AVAILABLE = False
    # Create mock classes to prevent errors
    class DeepgramClient:
        def __init__(self, *args, **kwargs):
            pass
    
    class PrerecordedOptions:
        def __init__(self, *args, **kwargs):
            pass
    
    FileSource = dict

# Configure Streamlit page
st.set_page_config(
    page_title="🎙️ Voice AI Agent",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Base: Apple-like glass aesthetic */
    .stApp {
        background: radial-gradient(1200px 600px at 10% 10%, rgba(255,255,255,0.06), transparent),
                    radial-gradient(1000px 500px at 90% 0%, rgba(255,255,255,0.05), transparent),
                    linear-gradient(180deg, #0b0f17 0%, #0a0d14 100%);
        color: #E6EAF2;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Sidebar as a frosted glass control center */
    [data-testid="stSidebar"] {
        backdrop-filter: blur(16px);
        background: rgba(255, 255, 255, 0.04);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }

    /* Header */
    .main-header {
        text-align: center;
        padding: 2.25rem 1.25rem;
        margin-bottom: 1.5rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35), inset 0 0 0 1px rgba(255,255,255,0.04);
        backdrop-filter: blur(14px);
    }
    .main-header h1 { font-weight: 700; letter-spacing: -0.02em; margin: 0; }
    .main-header p { opacity: 0.8; margin: .4rem 0 0; }

    /* Glass cards */
    .glass-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35), inset 0 1px rgba(255,255,255,0.05);
        backdrop-filter: blur(12px);
    }
    .section-title { font-size: 1.1rem; font-weight: 600; margin-bottom: .5rem; opacity: .9; }

    /* Chat bubbles */
    .chat-message {
        padding: 0.9rem 1rem;
        margin: 0.5rem 0;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    .user-message {
        background: linear-gradient(135deg, rgba(255,255,255,0.18), rgba(255,255,255,0.06));
        color: #0b0f17;
        border: 1px solid rgba(255,255,255,0.35);
    }
    .ai-message {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255,255,255,0.08);
    }

    /* Inputs & buttons */
    .stTextInput input, .stTextArea textarea, .stFileUploader, .stSelectbox select {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: #E6EAF2 !important;
        border-radius: 12px !important;
    }
    .stButton > button {
        background: linear-gradient(180deg, rgba(255,255,255,0.16), rgba(255,255,255,0.06));
        border: 1px solid rgba(255,255,255,0.22);
        color: #E6EAF2;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.3), inset 0 1px rgba(255,255,255,0.12);
    }
    .stButton > button:hover { transform: translateY(-1px); transition: all .2s ease; }

    /* Small status chips (if ever used later) */
    .status-chip { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.14); background: rgba(255,255,255,0.06); }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #25d366; box-shadow: 0 0 10px rgba(37,211,102,.6); }

    .transcription-box {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0 0;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'deepgram_client' not in st.session_state:
    st.session_state.deepgram_client = None
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False

def initialize_deepgram():
    """Initialize Deepgram client"""
    if not DEEPGRAM_AVAILABLE:
        # Silently skip in demo mode
        return False
        
    try:
        # Try to get API key from secrets first, then from user input
        api_key = None
        
        # Check Streamlit secrets
        try:
            api_key = st.secrets["DEEPGRAM_API_KEY"]
        except:
            pass
        
        # If no secrets, check environment
        if not api_key:
            api_key = os.getenv("DEEPGRAM_API_KEY")
        
        # If still no API key, ask user
        if not api_key:
            # No UI prompt; remain in demo mode gracefully
            return False
        
        if api_key and DEEPGRAM_AVAILABLE:
            st.session_state.deepgram_client = DeepgramClient(api_key)
            st.session_state.api_key_set = True
            return True
            
    except Exception as e:
        st.error(f"❌ Error initializing Deepgram: {str(e)}")
        return False
    
    return False

def transcribe_audio(audio_data):
    """Transcribe audio using Deepgram"""
    if not DEEPGRAM_AVAILABLE:
        return "Mock transcription: This is a demo transcription. Connect Deepgram API for real transcription."
    
    if not st.session_state.deepgram_client:
        # Fall back to mock when client isn't initialized
        return "Mock transcription: This is a demo transcription. Connect Deepgram API for real transcription."
    
    try:
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_data)
            tmp_file_path = tmp_file.name
        
        # Read the audio file
        with open(tmp_file_path, "rb") as audio_file:
            buffer_data = audio_file.read()
        
        payload = {
            "buffer": buffer_data,
        }
        
        # Configure Deepgram options
        options = PrerecordedOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            punctuate=True,
            paragraphs=True,
        )
        
        # Transcribe the audio
        response = st.session_state.deepgram_client.listen.prerecorded.v("1").transcribe_file(
            payload, options
        )
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        # Extract transcript
        if response.results and response.results.channels:
            transcript = response.results.channels[0].alternatives[0].transcript
            return transcript.strip() if transcript else "No speech detected"
        else:
            return "No transcript available"
            
    except Exception as e:
        # Clean up temporary file on error
        try:
            os.unlink(tmp_file_path)
        except:
            pass
        return f"Mock transcription due to error: {str(e)}"

def add_message(role, content):
    """Add a message to the chat history"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })

def display_chat_messages():
    """Display chat messages"""
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

def generate_ai_response(user_input):
    """Generate AI response (mock implementation)"""
    responses = [
        f"I heard you say: '{user_input}'. That's interesting! How can I help you further?",
        f"Thanks for sharing: '{user_input}'. What would you like to know more about?",
        f"I understand you mentioned: '{user_input}'. Let me know if you have any questions!",
        f"Great input: '{user_input}'. Is there anything specific you'd like me to help with?",
        f"I received your message: '{user_input}'. How else can I assist you today?"
    ]
    
    import random
    return random.choice(responses)

# Main App
def main():
    # Header
    st.markdown(
        """
        <div class="main-header">
            <h1>🎙️ Voice AI Agent</h1>
            <p>Elegant glass interface for voice and chat</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Sidebar
    with st.sidebar:
        st.markdown("#### Control Center")
        if st.button("� New Session", use_container_width=True):
            st.session_state.messages = []
            st.experimental_rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='glass-card'><div class='section-title'>🎙️ Voice Recording</div>", unsafe_allow_html=True)
        
        # Check if audio recorder is available
        if not AUDIO_RECORDER_AVAILABLE:
            st.warning("🎙️ Live audio recording not available. Use file upload or text input below.")
            
            # File upload alternative
            uploaded_file = st.file_uploader(
                "Upload an audio file:",
                type=['wav', 'mp3', 'ogg', 'm4a', 'flac'],
                help="Upload audio files for transcription"
            )
            
            audio = None
            if uploaded_file is not None:
                st.audio(uploaded_file)
                if st.button("🔄 Process Audio File"):
                    audio = uploaded_file.read()
        else:
            try:
                # Use audiorecorder
                audio = audiorecorder("🎤 Start Recording", "⏹️ Stop Recording")
            except Exception as e:
                st.error(f"Audio recorder error: {str(e)}")
                audio = None
        
        # Process audio when recorded
        if audio is not None and (
            (hasattr(audio, '__len__') and len(audio) > 0) or 
            (isinstance(audio, bytes) and len(audio) > 0)
        ):
            # Display audio player
            try:
                if hasattr(audio, 'export'):
                    st.audio(audio.export().read())
                    audio_bytes = audio.export().read()
                else:
                    st.audio(audio)
                    audio_bytes = audio
            except Exception as e:
                st.error(f"Audio display error: {str(e)}")
                audio_bytes = audio if isinstance(audio, bytes) else None
            
            # Transcribe audio
            if audio_bytes:
                with st.spinner("🔄 Transcribing audio..."):
                    try:
                        # Transcribe
                        transcript = transcribe_audio(audio_bytes)
                        
                        if transcript and transcript.strip() and transcript != "No speech detected":
                            # Add user message
                            add_message("user", transcript)
                            
                            # Generate AI response
                            ai_response = generate_ai_response(transcript)
                            add_message("assistant", ai_response)
                            
                            # Show success
                            st.success(f"✅ Transcribed: {transcript}")
                            
                            # Rerun to show new messages
                            st.rerun()
                        else:
                            st.warning("⚠️ No clear speech detected. Please try again.")
                            
                    except Exception as e:
                        st.error(f"❌ Error processing audio: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='glass-card'><div class='section-title'>📊 Session</div>", unsafe_allow_html=True)
        
        # Display statistics
        total_messages = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        ai_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        
        st.metric("Total Messages", total_messages)
        st.metric("Your Messages", user_messages)
        st.metric("AI Responses", ai_messages)
        
        # Latest transcription
        if st.session_state.messages:
            latest_user_msg = None
            for msg in reversed(st.session_state.messages):
                if msg["role"] == "user":
                    latest_user_msg = msg
                    break
            
            if latest_user_msg:
                st.markdown("<div class='section-title' style='margin-top:.5rem'>💬 Latest Transcription</div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="transcription-box">
                    <strong>Time:</strong> {latest_user_msg["timestamp"]}<br>
                    <strong>Text:</strong> {latest_user_msg["content"]}
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Chat display
    st.markdown("<div class='glass-card'><div class='section-title'>💬 Conversation</div>", unsafe_allow_html=True)
    
    if st.session_state.messages:
        # Create a container for messages with scroll
        with st.container():
            display_chat_messages()
    else:
        st.info("👋 Start by recording some audio above! Your conversation will appear here.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Text input as backup
    st.markdown("<div class='glass-card'><div class='section-title'>⌨️ Text Input (Alternative)</div>", unsafe_allow_html=True)
    text_input = st.text_input(
        "Type your message here:",
        placeholder="Enter text or use voice recording above..."
    )
    
    if st.button("📤 Send Text") and text_input:
        # Add user message
        add_message("user", text_input)
        
        # Generate AI response
        ai_response = generate_ai_response(text_input)
        add_message("assistant", ai_response)
        
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer info
    # Clean footer (no demo/status messaging)
    st.markdown("""
    <div style="opacity:.45; text-align:center; padding:1rem 0;">Made with ❤️ — minimal, elegant, and focused</div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()