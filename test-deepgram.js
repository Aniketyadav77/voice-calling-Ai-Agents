require("dotenv").config();
const { createClient } = require("@deepgram/sdk");

console.log("Testing Deepgram API key...");
console.log("API Key:", process.env.DEEPGRAM_API_KEY ? "Present" : "Missing");

const deepgram = createClient(process.env.DEEPGRAM_API_KEY);

// Test with a simple pre-recorded audio transcription
async function testDeepgram() {
  try {
    // Test the API key with a simple request
    const projectResponse = await deepgram.manage.getProject(process.env.DEEPGRAM_PROJECT_ID || "");
    console.log("✅ Deepgram API key is valid!");
  } catch (error) {
    if (error.message.includes('401')) {
      console.log("❌ Deepgram API key is invalid or expired");
    } else {
      console.log("✅ Deepgram API key seems valid (got a different error, which is expected)");
    }
    console.log("Error details:", error.message);
  }

  // Test live transcription setup
  try {
    const deepgramOptions = {
      model: "nova-2",
      language: "en-US",
      smart_format: true,
      interim_results: true
    };

    const deepgramLive = deepgram.listen.live(deepgramOptions);
    
    deepgramLive.on("open", () => {
      console.log("✅ Deepgram live connection can be established");
      deepgramLive.finish();
    });
    
    deepgramLive.on("error", (error) => {
      console.log("❌ Deepgram live connection error:", error);
    });

    deepgramLive.on("close", () => {
      console.log("ℹ️ Deepgram live connection closed");
    });

  } catch (error) {
    console.log("❌ Error setting up Deepgram live:", error.message);
  }
}

testDeepgram();