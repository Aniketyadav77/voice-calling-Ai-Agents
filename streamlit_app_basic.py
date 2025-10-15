import streamlit as st
import os
from datetime import datetime

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
    
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .success-box { background-color: #d4edda; color: #155724; }
    .warning-box { background-color: #fff3cd; color: #856404; }
    .error-box { background-color: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

def add_message(role, content):
    """Add a message to the chat history"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })

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

# Main App
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎙️ Voice AI Agent</h1>
        <p>AI-powered chat interface with text and voice support</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Controls")
        
        # Status
        st.markdown("""
        <div class="status-box success-box">
            <strong>✅ Status:</strong> Ready
        </div>
        """, unsafe_allow_html=True)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # Instructions
        st.markdown("### 📝 How to Use")
        st.markdown("""
        1. **Type Message**: Enter text in the input box below
        2. **Upload Audio**: Use the file uploader for audio files
        3. **Get Response**: The AI will respond to your input
        4. **View Chat**: See the conversation history
        """)
        
        # Features
        st.markdown("### ✨ Features")
        st.markdown("""
        - 💬 **Text Chat Interface**
        - 📁 **Audio File Upload**
        - 🤖 **AI Responses**
        - 📱 **Responsive Design**
        - 🎨 **Modern UI**
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Chat Interface")
        
        # Text input
        st.markdown("#### ⌨️ Text Input")
        text_input = st.text_input(
            "Type your message here:",
            placeholder="Enter your message and press Enter...",
            key="text_input"
        )
        
        col_send, col_clear = st.columns([1, 1])
        
        with col_send:
            if st.button("📤 Send Message", use_container_width=True, type="primary") and text_input:
                # Add user message
                add_message("user", text_input)
                
                # Generate AI response
                ai_response = generate_ai_response(text_input)
                add_message("assistant", ai_response)
                
                # Clear input and refresh
                st.rerun()
        
        with col_clear:
            if st.button("🔄 Clear Input", use_container_width=True):
                st.rerun()
        
        # Audio file upload
        st.markdown("#### 🎵 Audio Upload")
        uploaded_file = st.file_uploader(
            "Upload an audio file for transcription:",
            type=['wav', 'mp3', 'ogg', 'm4a', 'flac'],
            help="Upload audio files to simulate voice input"
        )
        
        if uploaded_file is not None:
            st.audio(uploaded_file)
            
            col_process, col_info = st.columns([1, 2])
            
            with col_process:
                if st.button("🔄 Process Audio", use_container_width=True):
                    # Simulate transcription
                    mock_transcript = f"[Simulated transcription of {uploaded_file.name}] This is a mock transcription for demonstration purposes."
                    
                    # Add to chat
                    add_message("user", mock_transcript)
                    ai_response = generate_ai_response(mock_transcript)
                    add_message("assistant", ai_response)
                    
                    st.success("✅ Audio processed successfully!")
                    st.rerun()
            
            with col_info:
                st.info("🔧 **Demo Mode**: This simulates audio transcription. Connect Deepgram API for real transcription.")
    
    with col2:
        st.markdown("### 📊 Chat Statistics")
        
        # Display statistics
        total_messages = len(st.session_state.messages)
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        ai_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        
        st.metric("Total Messages", total_messages)
        st.metric("Your Messages", user_messages)
        st.metric("AI Responses", ai_messages)
        
        # Recent activity
        if st.session_state.messages:
            st.markdown("### 🕒 Recent Activity")
            latest_msg = st.session_state.messages[-1]
            st.markdown(f"""
            <div class="status-box success-box">
                <strong>Last Message:</strong><br>
                {latest_msg['timestamp']} - {latest_msg['role'].title()}<br>
                <em>"{latest_msg['content'][:50]}..."</em>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat display
    st.markdown("---")
    st.markdown("### 💬 Conversation History")
    
    if st.session_state.messages:
        # Create a container for messages
        with st.container():
            display_chat_messages()
    else:
        st.markdown("""
        <div class="status-box warning-box">
            👋 <strong>Welcome!</strong> Start by typing a message above or uploading an audio file. 
            Your conversation will appear here.
        </div>
        """, unsafe_allow_html=True)
    
    # Footer with setup instructions
    st.markdown("---")
    with st.expander("🛠️ Setup Instructions for Full Features"):
        st.markdown("""
        ### To Enable Real Voice Transcription:
        
        1. **Get Deepgram API Key**:
           - Sign up at [Deepgram Console](https://console.deepgram.com/)
           - Generate a free API key
        
        2. **Add to Streamlit Secrets**:
           ```toml
           DEEPGRAM_API_KEY = "your_api_key_here"
           ```
        
        3. **Enable Audio Recording**:
           - The app will automatically detect available audio components
           - Or continue using file upload for audio input
        
        ### Current Mode:
        - ✅ Text chat fully functional
        - ✅ File upload working
        - ⚠️ Live audio recording requires additional setup
        - ⚠️ Real transcription requires Deepgram API key
        
        ### Deployment Status:
        - ✅ Basic Streamlit functionality
        - ✅ Responsive design
        - ✅ Chat interface
        - ✅ File handling
        """)

if __name__ == "__main__":
    main()