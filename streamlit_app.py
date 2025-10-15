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
        backdrop-filter: blur(10px);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left-color: #ffffff;
    }
    
    .ai-message {
        background: rgba(102, 126, 234, 0.1);
        border-left-color: #667eea;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-connected {
        background-color: #4CAF50;
        box-shadow: 0 0 10px #4CAF50;
    }
    
    .status-disconnected {
        background-color: #f44336;
    }
    
    .transcription-box {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
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
        st.error("❌ Deepgram SDK not available. Please check your requirements.txt")
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
            with st.sidebar:
                st.error("🔑 Deepgram API Key Required")
                api_key = st.text_input(
                    "Enter your Deepgram API Key:",
                    type="password",
                    help="Get your API key from https://console.deepgram.com/"
                )
                
                if api_key:
                    # Validate the API key format
                    if len(api_key) > 10:
                        os.environ["DEEPGRAM_API_KEY"] = api_key
                        st.success("✅ API Key set successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid API key format")
                        return False
                else:
                    st.warning("Please enter your Deepgram API key to continue")
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
        return "Error: Deepgram client not initialized"
    
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
    demo_text = " (Demo Mode)" if not DEEPGRAM_AVAILABLE else ""
    st.markdown(f"""
    <div class="main-header">
        <h1>🎙️ Voice AI Agent{demo_text}</h1>
        <p>{"AI-powered chat interface with voice support" if not DEEPGRAM_AVAILABLE else "Real-time speech transcription powered by Deepgram AI"}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize Deepgram
    if not DEEPGRAM_AVAILABLE:
        st.warning("⚠️ **Demo Mode**: Deepgram SDK not installed. Using mock transcriptions.")
        st.session_state.api_key_set = False
    else:
        if not st.session_state.api_key_set:
            if not initialize_deepgram():
                st.info("💡 **Info**: Enter your Deepgram API key in the sidebar for real transcription, or continue in demo mode.")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Controls")
        
        # Connection status
        if DEEPGRAM_AVAILABLE:
            status_color = "connected" if st.session_state.api_key_set else "disconnected"
            status_text = "Connected" if st.session_state.api_key_set else "Disconnected"
        else:
            status_color = "disconnected"
            status_text = "Demo Mode"
        
        st.markdown(f"""
        <div>
            <span class="status-indicator status-{status_color}"></span>
            <strong>Status:</strong> {status_text}
        </div>
        """, unsafe_allow_html=True)
        
        # Show SDK availability
        if DEEPGRAM_AVAILABLE:
            st.success("✅ Deepgram SDK Available")
        else:
            st.error("❌ Deepgram SDK not available")
            st.info("📦 Install deepgram-sdk for real transcription")
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Instructions
        st.markdown("### 📝 Instructions")
        st.markdown("""
        1. **Record Audio**: Click the record button below
        2. **Speak Clearly**: Talk into your microphone
        3. **Stop Recording**: Click stop when finished
        4. **View Transcription**: See the text appear automatically
        5. **Chat**: The AI will respond to your input
        """)
        
        # Features
        st.markdown("### ✨ Features")
        st.markdown("""
        - 🎙️ **Real-time Transcription**
        - 🤖 **AI Chat Interface** 
        - 📱 **Responsive Design**
        - 🔒 **Secure API Integration**
        - 🎨 **Modern UI/UX**
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎙️ Voice Recording")
        
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
    
    with col2:
        st.markdown("### 📊 Stats")
        
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
                st.markdown("### 💬 Latest Transcription")
                st.markdown(f"""
                <div class="transcription-box">
                    <strong>Time:</strong> {latest_user_msg["timestamp"]}<br>
                    <strong>Text:</strong> {latest_user_msg["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat display
    st.markdown("### 💬 Conversation")
    
    if st.session_state.messages:
        # Create a container for messages with scroll
        with st.container():
            display_chat_messages()
    else:
        st.info("👋 Start by recording some audio above! Your conversation will appear here.")
    
    # Text input as backup
    st.markdown("### ⌨️ Text Input (Alternative)")
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
    
    # Footer info
    st.markdown("---")
    if not DEEPGRAM_AVAILABLE:
        st.info("""
        🚀 **You're in Demo Mode!** The app is working perfectly. 
        
        **Current Features:**
        - ✅ Text chat with AI responses
        - ✅ File upload for audio files  
        - ✅ Modern responsive interface
        - ✅ Message history and statistics
        
        **To enable live voice recording and real transcription:**
        1. Add `deepgram-sdk>=3.0.0` and `streamlit-audiorecorder>=0.0.5` to requirements.txt
        2. Get a free Deepgram API key from https://console.deepgram.com/
        3. Add it to Streamlit secrets or environment variables
        """)

if __name__ == "__main__":
    main()