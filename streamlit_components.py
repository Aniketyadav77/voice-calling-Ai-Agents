import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import plotly.graph_objects as go
import plotly.express as px

def create_audio_visualizer(audio_data=None):
    """Create an audio visualizer component"""
    if audio_data is None:
        # Create a placeholder visualization
        fig = go.Figure()
        
        # Create some sample waveform data
        x = np.linspace(0, 2*np.pi, 100)
        y = np.sin(x) * np.random.random(100) * 0.5
        
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Audio Waveform',
            line=dict(color='#667eea', width=2)
        ))
        
        fig.update_layout(
            title="🎵 Audio Visualizer",
            xaxis_title="Time",
            yaxis_title="Amplitude", 
            template="plotly_dark",
            height=300,
            showlegend=False
        )
        
        return fig
    else:
        # Create visualization from actual audio data
        # This would be implemented based on the audio format
        pass

def create_transcription_confidence_chart(confidence_scores):
    """Create a confidence score chart for transcriptions"""
    if not confidence_scores:
        confidence_scores = [0.95, 0.87, 0.92, 0.98, 0.84]  # Sample data
    
    fig = px.bar(
        x=list(range(len(confidence_scores))),
        y=confidence_scores,
        title="📊 Transcription Confidence Scores",
        labels={'x': 'Word Index', 'y': 'Confidence'},
        color=confidence_scores,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        template="plotly_dark",
        height=250,
        showlegend=False
    )
    
    return fig

def show_real_time_status():
    """Display real-time status indicators"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎙️ Microphone",
            value="Active",
            delta="Recording"
        )
    
    with col2:
        st.metric(
            label="🔗 Connection", 
            value="Connected",
            delta="Deepgram API"
        )
    
    with col3:
        st.metric(
            label="⚡ Latency",
            value="< 100ms",
            delta="Real-time"
        )
    
    with col4:
        st.metric(
            label="🎯 Accuracy",
            value="95%",
            delta="High Quality"
        )

def create_voice_controls():
    """Create voice control interface"""
    st.markdown("### 🎛️ Voice Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎤 Start Recording", use_container_width=True, type="primary"):
            st.session_state.recording = True
            st.success("Recording started...")
    
    with col2:
        if st.button("⏸️ Pause", use_container_width=True):
            st.session_state.recording = False  
            st.warning("Recording paused...")
    
    with col3:
        if st.button("⏹️ Stop", use_container_width=True):
            st.session_state.recording = False
            st.info("Recording stopped...")

def display_transcription_history():
    """Display transcription history with timestamps"""
    if 'transcription_history' not in st.session_state:
        st.session_state.transcription_history = []
    
    st.markdown("### 📜 Transcription History")
    
    if st.session_state.transcription_history:
        for i, entry in enumerate(reversed(st.session_state.transcription_history[-10:])):  # Show last 10
            with st.expander(f"Transcription {len(st.session_state.transcription_history)-i}: {entry['timestamp']}"):
                st.write(f"**Text:** {entry['text']}")
                st.write(f"**Confidence:** {entry.get('confidence', 'N/A')}")
                st.write(f"**Duration:** {entry.get('duration', 'N/A')} seconds")
    else:
        st.info("No transcriptions yet. Start recording to see your speech-to-text results here!")

def create_settings_panel():
    """Create settings panel for the application"""
    with st.sidebar.expander("⚙️ Settings"):
        st.markdown("#### Audio Settings")
        
        # Sample rate selection
        sample_rate = st.selectbox(
            "Sample Rate",
            options=[16000, 44100, 48000],
            index=0,
            help="Audio sample rate in Hz"
        )
        
        # Language selection
        language = st.selectbox(
            "Language", 
            options=["en-US", "en-GB", "es-ES", "fr-FR", "de-DE"],
            index=0,
            help="Speech recognition language"
        )
        
        # Model selection
        model = st.selectbox(
            "Deepgram Model",
            options=["nova-2", "nova", "enhanced", "base"],
            index=0,
            help="Deepgram transcription model"
        )
        
        st.markdown("#### UI Settings")
        
        # Theme toggle
        dark_mode = st.toggle("🌙 Dark Mode", value=True)
        
        # Auto-scroll
        auto_scroll = st.toggle("📜 Auto-scroll Chat", value=True)
        
        # Show confidence scores
        show_confidence = st.toggle("📊 Show Confidence Scores", value=False)
        
        return {
            "sample_rate": sample_rate,
            "language": language,
            "model": model,
            "dark_mode": dark_mode,
            "auto_scroll": auto_scroll,
            "show_confidence": show_confidence
        }