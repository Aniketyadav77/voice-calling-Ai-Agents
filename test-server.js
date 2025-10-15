const express = require('express');
const app = express();

// Test endpoint to simulate a call
app.get('/test-call', (req, res) => {
  res.set('Content-Type', 'text/xml');
  res.send(`
    <Response>
      <Start>
        <Stream url="wss://melia-uniteable-uninfinitely.ngrok-free.dev/"/>
      </Start>
      <Say>Testing voice AI transcription. This is a test message for transcription.</Say>
      <Pause length="10" />
      <Say>End of test</Say>
    </Response>
  `);
});

app.listen(8081, () => {
  console.log('Test server running on port 8081');
  console.log('Test URL: http://localhost:8081/test-call');
});