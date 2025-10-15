const fs = require('fs');
const WebSocket = require('ws');

// Create a simple audio buffer for testing (simulate audio data)
function createTestAudioBuffer() {
    // Generate a simple sine wave as test audio
    const sampleRate = 8000;
    const duration = 3; // 3 seconds
    const frequency = 440; // A4 note
    const samples = sampleRate * duration;
    const buffer = Buffer.alloc(samples);
    
    for (let i = 0; i < samples; i++) {
        const sample = Math.sin(2 * Math.PI * frequency * i / sampleRate) * 127 + 128;
        buffer[i] = Math.floor(sample);
    }
    
    return buffer;
}

// Test the WebSocket connection with audio data
function testWebSocketWithAudio() {
    const ws = new WebSocket('ws://localhost:8080');
    
    ws.on('open', function() {
        console.log('✅ Connected to WebSocket');
        
        // Send connected event
        ws.send(JSON.stringify({
            event: "connected"
        }));
        
        setTimeout(() => {
            // Send start event
            ws.send(JSON.stringify({
                event: "start",
                streamSid: "test-browser-stream"
            }));
            
            // Generate and send test audio data
            const audioBuffer = createTestAudioBuffer();
            const base64Audio = audioBuffer.toString('base64');
            
            // Send audio in chunks
            const chunkSize = 160; // Typical for 8kHz MULAW
            for (let i = 0; i < base64Audio.length; i += chunkSize) {
                const chunk = base64Audio.substring(i, i + chunkSize);
                
                setTimeout(() => {
                    ws.send(JSON.stringify({
                        event: "media",
                        media: {
                            payload: chunk
                        }
                    }));
                }, i / chunkSize * 20); // Send every 20ms
            }
            
            // Send stop event after audio finishes
            setTimeout(() => {
                ws.send(JSON.stringify({
                    event: "stop"
                }));
                
                setTimeout(() => {
                    ws.close();
                    console.log('✅ Test completed');
                }, 1000);
            }, 5000);
            
        }, 1000);
    });
    
    ws.on('message', function(data) {
        const message = JSON.parse(data);
        if (message.event === 'interim-transcription') {
            console.log('📝 Transcription:', message.text);
        }
    });
    
    ws.on('error', function(error) {
        console.error('❌ WebSocket error:', error);
    });
}

console.log('🧪 Starting WebSocket audio test...');
testWebSocketWithAudio();