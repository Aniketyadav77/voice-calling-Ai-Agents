# 🎙️ Voice AI Agent - Real-Time Transcription & Chat Interface

> A modern voice-powered AI agent with real-time speech transcription, built with Twilio Media Streams and Deepgram AI. Features a sleek chat interface inspired by modern AI assistants.

[![Node.js](https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)
[![Express.js](https://img.shields.io/badge/Express.js-404D59?style=for-the-badge)](https://expressjs.com/)
[![Twilio](https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=Twilio&logoColor=white)](https://www.twilio.com/)
[![Deepgram](https://img.shields.io/badge/Deepgram-13EF93?style=for-the-badge&logo=deepgram&logoColor=white)](https://deepgram.com/)
[![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=socketdotio&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

## 🌟 Features

- **Real-time Voice Transcription** - Live speech-to-text using Deepgram AI
- **Modern Chat Interface** - Glassmorphic UI inspired by ChatGPT and Gemini
- **Phone Call Integration** - Transcribe phone calls via Twilio Media Streams
- **Browser Voice Input** - Direct microphone access for web-based interactions
- **Multiple UI Options** - Choose from chat, futuristic, or comparison interfaces
- **WebSocket Streaming** - Low-latency audio processing and real-time updates
- **Responsive Design** - Works seamlessly on desktop and mobile devices

## 🚀 Live Demo

```bash
# Clone and run locally
git clone https://github.com/Aniketyadav77/voice-calling-Ai-Agents.git
cd voice-calling-Ai-Agents
npm install
npm start
```

Visit `http://localhost:8080` to experience the AI chat interface.

## 📋 Prerequisites

Before getting started, ensure you have:

- **Node.js** (v14 or higher)
- **Twilio Account** - [Sign up for free](https://www.twilio.com/try-twilio)
- **Deepgram Account** - [Get your API key](https://deepgram.com/)
- **ngrok** - [Download here](https://ngrok.com/download)

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Aniketyadav77/voice-calling-Ai-Agents.git
cd voice-calling-Ai-Agents
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
DEEPGRAM_API_KEY=your_deepgram_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
```

### 4. Get Your API Keys

#### Deepgram Setup
1. Create account at [Deepgram Console](https://console.deepgram.com/)
2. Generate an API key from your dashboard
3. Add the key to your `.env` file

#### Twilio Setup
1. Sign up for [Twilio](https://www.twilio.com/try-twilio)
2. Find your Account SID and Auth Token in the console
3. Purchase a phone number for voice calls (optional for phone integration)

### 5. Start the Application

```bash
# Development mode
npm start

# Or directly
node index-fixed.js
```

The server will start on `http://localhost:8080`

### 6. Enable Phone Call Transcription (Optional)

For phone call integration, set up ngrok tunnel:

```bash
# Install ngrok and authenticate
ngrok authtoken YOUR_NGROK_TOKEN
ngrok http 8080
```

Configure your Twilio phone number webhook to point to your ngrok URL.

## 🎯 Usage

### Web Interface
1. Open `http://localhost:8080` in your browser
2. Click the microphone button to start voice recording
3. Speak and see real-time transcription appear
4. Use the chat interface to interact with the AI

### Phone Integration
1. Call your Twilio phone number
2. Speech will be transcribed live in the web interface
3. View transcription results in real-time

### Available Interfaces
- `/` - Main AI Chat Interface (Recommended)
- `/futuristic` - Glassmorphic UI with visualizers
- `/comparison` - Side-by-side comparison view
- `/simple` - Minimal testing interface

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Browser UI    │◄──►│   Node.js Server │◄──►│   Deepgram AI   │
│  (WebSocket)    │    │   (Express + WS) │    │ (Live Streaming)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        ▲
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌──────────────────┐
│ Media Recorder  │    │ Twilio Media     │
│   (Browser)     │    │   Streams        │
└─────────────────┘    └──────────────────┘
```

## 🛠️ Technical Stack

- **Backend**: Node.js, Express.js, WebSocket
- **Speech-to-Text**: Deepgram Live Streaming API
- **Telephony**: Twilio Media Streams
- **Frontend**: Vanilla JavaScript, CSS3, HTML5
- **Real-time Communication**: WebSocket protocol
- **Audio Processing**: MediaRecorder API, Base64 encoding

## 📁 Project Structure

```
voice-calling-Ai-Agents/
├── index-fixed.js          # Main server with enhanced error handling
├── ai-chat-ui.html         # Primary chat interface
├── futuristic-ui.html      # Alternative glassmorphic UI
├── package.json            # Dependencies and scripts
├── .env.sample             # Environment variables template
├── public/                 # Static assets
│   ├── background.jpg      # Background images
│   └── background2.jpg
├── test-scripts/           # Development testing utilities
│   ├── test-deepgram.js    # Deepgram API validation
│   ├── test-websocket.js   # WebSocket connection test
│   └── configure-webhook.js # Twilio webhook helper
└── README.md               # This file
```

## 🔧 Configuration Options

### Server Settings
- **Port**: Default 8080 (configurable via `PORT` environment variable)
- **WebSocket**: Automatic upgrade from HTTP connections
- **CORS**: Enabled for cross-origin requests

### Audio Settings
- **Sample Rate**: 16kHz (optimized for Deepgram)
- **Encoding**: Base64 for WebSocket transmission
- **Format**: WebM/Opus (browser) → Linear16 (Deepgram)

### Deepgram Configuration
- **Model**: Nova-2 (latest and most accurate)
- **Features**: Real-time streaming, punctuation, smart formatting
- **Language**: English (configurable)

## 🧪 Testing

Run the included test scripts to validate your setup:

```bash
# Test Deepgram API connectivity
node test-deepgram.js

# Test WebSocket server
node test-websocket.js

# Validate server endpoints
node test-server.js
```

## 🚀 Deployment

### Local Development
```bash
npm start
```

### Production Deployment
1. Set up environment variables on your hosting platform
2. Configure webhook URLs for production domain
3. Enable HTTPS for secure WebSocket connections
4. Set up proper error monitoring and logging

### Hosting Platforms
- **Heroku**: Ready for deployment with included `Procfile`
- **Vercel**: Works with serverless functions
- **Railway**: Simple deployment with automatic builds
- **DigitalOcean**: App Platform compatible

## 🔒 Security Considerations

- Store API keys securely in environment variables
- Use HTTPS in production for secure WebSocket connections
- Validate and sanitize all user inputs
- Implement rate limiting for API calls
- Monitor usage to prevent API quota exceeded

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the ISC License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Twilio](https://www.twilio.com/) - For Media Streams API
- [Deepgram](https://deepgram.com/) - For AI-powered speech recognition
- [Express.js](https://expressjs.com/) - For the web framework
- Original concept inspired by Twilio's media streams examples

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/Aniketyadav77/voice-calling-Ai-Agents/issues) page
2. Create a new issue with detailed description
3. Include error logs and system information

---

**Made with ❤️ by [Aniket Yadav](https://github.com/Aniketyadav77)**

> Transform voice into intelligent conversations with modern AI technology