const WebSocket = require('ws');

console.log('🧪 Testing WebSocket connection...');

const ws = new WebSocket('ws://localhost:8080');

ws.on('open', function() {
    console.log('✅ WebSocket connected');
    
    // Test the flow
    console.log('📤 Sending connected event...');
    ws.send(JSON.stringify({
        event: "connected"
    }));
    
    setTimeout(() => {
        console.log('📤 Sending start event...');
        ws.send(JSON.stringify({
            event: "start",
            streamSid: "test-stream-123"
        }));
        
        // Send some test text as if it were audio
        setTimeout(() => {
            console.log('📤 Sending test message...');
            // Simulate sending some audio data
            const testMessage = "Hello world test";
            const testBuffer = Buffer.from(testMessage);
            const base64Data = testBuffer.toString('base64');
            
            ws.send(JSON.stringify({
                event: "media",
                media: {
                    payload: base64Data
                }
            }));
            
            // Stop after a bit
            setTimeout(() => {
                console.log('📤 Sending stop event...');
                ws.send(JSON.stringify({
                    event: "stop"
                }));
                
                setTimeout(() => {
                    ws.close();
                }, 1000);
            }, 3000);
            
        }, 1000);
    }, 1000);
});

ws.on('message', function(data) {
    const message = JSON.parse(data);
    console.log('📥 Received:', message);
});

ws.on('error', function(error) {
    console.error('❌ WebSocket error:', error);
});

ws.on('close', function() {
    console.log('🔒 WebSocket connection closed');
});