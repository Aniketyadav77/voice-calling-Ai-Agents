const WebSocket = require("ws");
const express = require("express");
const app = express();
const server = require("http").createServer(app);
const wss = new WebSocket.Server({ server });

const path = require("path");

require("dotenv").config();

//Include Deepgram SDK
const { createClient } = require("@deepgram/sdk");
const deepgram = createClient(process.env.DEEPGRAM_API_KEY);

//Configure Deepgram options
const deepgramOptions = {
  model: "nova-2",
  language: "en-US",
  smart_format: true,
  interim_results: true,
  endpointing: 300,
  encoding: "linear16",
  sample_rate: 16000,
  channels: 1
};

wss.on("connection", function connection(ws) {
  console.log("New Connection Initiated");

  let deepgramLive = null;

  ws.on("message", function incoming(message) {
    const msg = JSON.parse(message);
    switch (msg.event) {
      case "connected":
        console.log(`A new call has connected.`);
        break;
      case "start":
        console.log(`Starting Media Stream ${msg.streamSid}`);
        
        // Create Deepgram live transcription connection
        try {
          deepgramLive = deepgram.listen.live(deepgramOptions);
          
          // Handle connection open
          deepgramLive.on("open", () => {
            console.log("Deepgram connection opened");
          });
          
          // Handle transcription results - Updated event name
          deepgramLive.on("transcript", (data) => {
            console.log("Received transcript data:", data);
            try {
              const transcript = data.channel?.alternatives?.[0]?.transcript || data.alternatives?.[0]?.transcript;
              if (transcript && transcript.length > 0) {
                console.log("Transcript:", transcript);
                wss.clients.forEach((client) => {
                  if (client.readyState === WebSocket.OPEN) {
                    client.send(
                      JSON.stringify({
                        event: "interim-transcription",
                        text: transcript,
                      })
                    );
                  }
                });
              }
            } catch (transcriptError) {
              console.error("Error processing transcript:", transcriptError);
            }
          });

          // Handle errors
          deepgramLive.on("error", (error) => {
            console.error("Deepgram error:", error);
          });

          // Handle connection close
          deepgramLive.on("close", (closeEvent) => {
            console.log("Deepgram connection closed:", closeEvent);
          });

          // Handle warnings
          deepgramLive.on("warning", (warning) => {
            console.warn("Deepgram warning:", warning);
          });
          
        } catch (error) {
          console.error("Error creating Deepgram connection:", error);
        }
        break;
      case "media":
        // Send audio data to Deepgram
        try {
          if (deepgramLive && deepgramLive.getReadyState() === 1) {
            // Convert base64 to buffer for Deepgram
            const audioBuffer = Buffer.from(msg.media.payload, 'base64');
            deepgramLive.send(audioBuffer);
          } else {
            console.log("Deepgram not ready, ready state:", deepgramLive?.getReadyState());
          }
        } catch (error) {
          console.error("Error sending audio to Deepgram:", error);
        }
        break;
      case "stop":
        console.log(`Call Has Ended`);
        if (deepgramLive) {
          deepgramLive.finish();
          deepgramLive = null;
        }
        break;
    }
  });
});

app.use(express.static("public"));

app.get("/", (req, res) => res.sendFile(path.join(__dirname, "/index.html")));

app.get("/browser-test", (req, res) => res.sendFile(path.join(__dirname, "/browser-test.html")));

app.get("/test-ui", (req, res) => res.sendFile(path.join(__dirname, "/test.html")));

app.get("/test", (req, res) => {
  res.set("Content-Type", "text/xml");
  res.send(`
    <Response>
      <Start>
        <Stream url="wss://${req.headers.host}/"/>
      </Start>
      <Say>Testing voice AI transcription system. This is a browser based test.</Say>
      <Pause length="10" />
      <Say>End of test message.</Say>
    </Response>
  `);
});

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

console.log("Listening on Port 8080");
server.listen(8080);
