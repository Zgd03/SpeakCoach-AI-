import { ref } from "vue";

export function useWebSocket() {
  const ws = ref(null);
  const connected = ref(false);
  const messages = ref([]); // { role, content, corrections[], audioData? }
  const currentCorrections = ref([]);
  const currentScores = ref(null);
  const error = ref(null);
  const audioPlaying = ref(false);

  let pendingResolve = null;
  let audioQueue = Promise.resolve(); // promise-chain for sequential playback

  function connect(url) {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const fullUrl = `${protocol}//${host}${url}`;

    ws.value = new WebSocket(fullUrl);

    ws.value.onopen = () => {
      connected.value = true;
      error.value = null;
    };

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case "ai_reply":
          // Store audio data on the assistant message for replay
          if (data.audio) {
            messages.value.push({
              role: "assistant",
              content: data.text,
              corrections: [],
              audioData: data.audio, // store for replay
            });
            // Play audio via queue (sequential)
            enqueueAudio(data.audio);
          } else {
            messages.value.push({
              role: "assistant",
              content: data.text,
              corrections: [],
              audioData: null,
            });
          }
          if (pendingResolve) {
            pendingResolve(data);
            pendingResolve = null;
          }
          break;

        case "correction":
          currentCorrections.value = data.data;
          // Attach corrections to the last user message
          const lastMsg = messages.value[messages.value.length - 1];
          if (lastMsg && lastMsg.role === "user") {
            lastMsg.corrections = data.data;
          }
          break;

        case "score_update":
          currentScores.value = data.data;
          break;

        case "error":
          error.value = data.message;
          break;
      }
    };

    ws.value.onclose = () => {
      connected.value = false;
    };

    ws.value.onerror = () => {
      error.value = "WebSocket 连接失败";
      connected.value = false;
    };
  }

  function sendMessage(text) {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      messages.value.push({
        role: "user",
        content: text,
        corrections: [],
      });
      ws.value.send(JSON.stringify({ type: "user_message", text }));
    }
  }

  /**
   * Play audio from base64 data, returns a promise that resolves when done.
   */
  function _playAudioOnce(base64Data) {
    return new Promise((resolve) => {
      try {
        const binaryStr = atob(base64Data);
        const bytes = new Uint8Array(binaryStr.length);
        for (let i = 0; i < binaryStr.length; i++) {
          bytes[i] = binaryStr.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: "audio/mp3" });
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);

        audio.onended = () => {
          URL.revokeObjectURL(url);
          resolve();
        };
        audio.onerror = () => {
          URL.revokeObjectURL(url);
          resolve(); // resolve anyway to unblock queue
        };

        // Try to play; if autoplay blocked, set playing=false and resolve
        audio.play().catch((e) => {
          URL.revokeObjectURL(url);
          console.warn("Audio playback blocked:", e.message);
          resolve();
        });
      } catch (e) {
        console.error("Audio decode failed:", e);
        resolve();
      }
    });
  }

  /**
   * Queue audio playback sequentially to avoid overlap.
   */
  function enqueueAudio(base64Data) {
    audioPlaying.value = true;
    audioQueue = audioQueue.then(() => _playAudioOnce(base64Data)).then(() => {
      audioPlaying.value = false;
    });
  }

  /**
   * Replay audio for a specific message index.
   */
  function replayAudio(index) {
    const msg = messages.value[index];
    if (!msg || !msg.audioData) return;
    audioPlaying.value = true;
    // Play independently (don't block the main queue)
    _playAudioOnce(msg.audioData).then(() => {
      audioPlaying.value = false;
    });
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close();
    }
  }

  return {
    connected,
    messages,
    currentCorrections,
    currentScores,
    error,
    audioPlaying,
    connect,
    sendMessage,
    replayAudio,
    disconnect,
  };
}
