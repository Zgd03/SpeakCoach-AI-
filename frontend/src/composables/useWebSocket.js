import { ref } from "vue";

export function useWebSocket() {
  const ws = ref(null);
  const connected = ref(false);
  const messages = ref([]); // { role, content, corrections[] }
  const currentCorrections = ref([]);
  const currentScores = ref(null);
  const error = ref(null);

  let pendingResolve = null;

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
          messages.value.push({
            role: "assistant",
            content: data.text,
            corrections: [],
          });
          // Play audio
          if (data.audio) {
            playAudio(data.audio);
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

  function playAudio(base64Data) {
    try {
      const binaryStr = atob(base64Data);
      const bytes = new Uint8Array(binaryStr.length);
      for (let i = 0; i < binaryStr.length; i++) {
        bytes[i] = binaryStr.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: "audio/mp3" });
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.onended = () => URL.revokeObjectURL(url);
      audio.play().catch(() => {
        // Autoplay may be blocked, user interaction needed
      });
    } catch (e) {
      console.error("Audio playback failed:", e);
    }
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
    connect,
    sendMessage,
    disconnect,
  };
}
