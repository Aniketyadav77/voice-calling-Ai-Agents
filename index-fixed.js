const WebSocket = require("ws");
const express = require("express");
const app = express();
const server = require("http").createServer(app);
const wss = new WebSocket.Server({ server });
const path = require("path");

require("dotenv").config();

// Include Deepgram SDK
const { createClient } = require("@deepgram/sdk");
const deepgram = createClient(process.env.DEEPGRAM_API_KEY);

console.log("Deepgram API Key:", process.env.DEEPGRAM_API_KEY ? "Present" : "Missing");

wss.on("connection", function connection(ws) {
  console.log("New Connection Initiated");
  let deepgramLive = null;

  ws.on("message", function incoming(message) {
    const msg = JSON.parse(message);
    console.log("Received message:", msg.event);

    switch (msg.event) {
      case "connected":
        console.log(`A new call has connected.`);
        break;
        
      case "start":
        console.log(`Starting Media Stream ${msg.streamSid}`);
        
        try {
          // Updated Deepgram configuration for browser audio
          const deepgramOptions = {
            model: "nova-2",
            language: "en-US",
            smart_format: true,
            interim_results: true,
            punctuate: true,
            encoding: "webm",
            sample_rate: 16000,
            channels: 1
          };

          deepgramLive = deepgram.listen.live(deepgramOptions);

          deepgramLive.on("open", () => {
            console.log("✅ Deepgram connection opened successfully");
          });

          // Handle multiple event types for compatibility
          deepgramLive.on("transcript", (data) => {
            handleTranscript(data);
          });

          deepgramLive.on("transcriptReceived", (data) => {
            handleTranscript(data);
          });

          deepgramLive.on("Results", (data) => {
            handleTranscript(data);
          });

          function handleTranscript(data) {
            console.log("📝 Raw transcript data:", JSON.stringify(data, null, 2));
            
            let transcript = null;
            let isInterim = false;
            
            // Handle different response formats
            if (data.channel && data.channel.alternatives && data.channel.alternatives[0]) {
              transcript = data.channel.alternatives[0].transcript;
              isInterim = data.is_final === false;
            } else if (data.results && data.results[0] && data.results[0].alternatives && data.results[0].alternatives[0]) {
              transcript = data.results[0].alternatives[0].transcript;
              isInterim = data.results[0].is_final === false;
            } else if (data.alternatives && data.alternatives[0]) {
              transcript = data.alternatives[0].transcript;
            } else if (typeof data === 'string') {
              transcript = data;
            }
            
            if (transcript && transcript.trim().length > 0) {
              console.log("✅ Sending transcript:", transcript);
              
              // Broadcast to all connected WebSocket clients
              wss.clients.forEach((client) => {
                if (client.readyState === WebSocket.OPEN) {
                  client.send(JSON.stringify({
                    event: "interim-transcription",
                    text: transcript,
                    is_interim: isInterim
                  }));
                }
              });
            }
          }

          deepgramLive.on("error", (error) => {
            console.error("❌ Deepgram error:", error);
            // Try to reconnect
            setTimeout(() => {
              if (deepgramLive && deepgramLive.getReadyState() === 3) {
                console.log("🔄 Attempting to reconnect to Deepgram...");
                // Don't create new connection here, just log
              }
            }, 1000);
          });

          deepgramLive.on("warning", (warning) => {
            console.warn("⚠️ Deepgram warning:", warning);
          });

          deepgramLive.on("close", (event) => {
            console.log("🔒 Deepgram connection closed:", event);
          });

        } catch (error) {
          console.error("❌ Error creating Deepgram connection:", error);
        }
        break;

      case "media":
        if (deepgramLive) {
          try {
            const readyState = deepgramLive.getReadyState();
            
            if (readyState === 1) { // OPEN
              // Convert base64 audio to buffer
              const audioBuffer = Buffer.from(msg.media.payload, 'base64');
              
              // Only log every 10th chunk to reduce spam
              if (Math.random() < 0.1) {
                console.log("📤 Sending audio chunk, size:", audioBuffer.length);
              }
              
              deepgramLive.send(audioBuffer);
              
            } else if (readyState === 0) { // CONNECTING
              // Wait for connection, don't spam logs
              if (Math.random() < 0.01) {
                console.log("⏳ Deepgram still connecting...");
              }
            } else if (readyState === 3) { // CLOSED
              console.log("🔄 Deepgram connection closed, attempting restart...");
              // Try to create a new connection
              try {
                const deepgramOptions = {
                  model: "nova-2",
                  language: "en-US",
                  smart_format: true,
                  interim_results: true,
                  punctuate: true,
                  encoding: "webm",
                  sample_rate: 16000,
                  channels: 1
                };
                
                deepgramLive = deepgram.listen.live(deepgramOptions);
                console.log("🔄 New Deepgram connection created");
              } catch (error) {
                console.error("❌ Error recreating Deepgram connection:", error);
              }
            }
            
          } catch (error) {
            console.error("❌ Error sending audio to Deepgram:", error);
          }
        } else {
          console.log("⚠️ Deepgram connection not initialized");
        }
        break;

      case "stop":
        console.log(`Call Has Ended`);
        if (deepgramLive) {
          try {
            deepgramLive.finish();
            deepgramLive = null;
          } catch (error) {
            console.error("Error closing Deepgram connection:", error);
          }
        }
        break;
    }
  });

  ws.on("close", () => {
    console.log("WebSocket connection closed");
    if (deepgramLive) {
      try {
        deepgramLive.finish();
      } catch (error) {
        console.error("Error closing Deepgram on WebSocket close:", error);
      }
    }
  });
});

app.use(express.static("public"));

app.get("/", (req, res) => res.sendFile(path.join(__dirname, "/ai-chat-ui.html")));

app.get("/futuristic", (req, res) => res.sendFile(path.join(__dirname, "/futuristic-ui.html")));

app.get("/old", (req, res) => res.sendFile(path.join(__dirname, "/index.html")));

app.get("/comparison", (req, res) => res.sendFile(path.join(__dirname, "/comparison-test.html")));

app.get("/simple", (req, res) => res.sendFile(path.join(__dirname, "/simple-test.html")));

app.get("/test-ui", (req, res) => res.sendFile(path.join(__dirname, "/test.html")));

app.post("/", (req, res) => {
  res.set("Content-Type", "text/xml");
  res.send(`
    <Response>
      <Start>
        <Stream url="wss://${req.headers.host}/"/>
      </Start>
      <Say>I will stream the next 60 seconds of audio through your websocket</Say>
      <Pause length="60" />
    </Response>
  `);
});

console.log("🚀 Server starting on Port 8080");
server.listen(8080);