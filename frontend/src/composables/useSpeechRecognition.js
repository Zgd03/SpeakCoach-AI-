import { ref } from "vue";

export function useSpeechRecognition() {
  const isSupported =
    "webkitSpeechRecognition" in window || "SpeechRecognition" in window;
  const isListening = ref(false);
  const transcript = ref("");
  const error = ref(null);

  let recognition = null;

  function start() {
    if (!isSupported) {
      error.value = "您的浏览器不支持语音识别，请使用 Chrome 或 Edge。";
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const result = event.results[0][0].transcript;
      transcript.value = result;
      isListening.value = false;
    };

    recognition.onerror = (event) => {
      error.value = `语音识别错误: ${event.error}`;
      isListening.value = false;
    };

    recognition.onend = () => {
      isListening.value = false;
    };

    isListening.value = true;
    error.value = null;
    transcript.value = "";
    recognition.start();
  }

  function stop() {
    if (recognition) {
      recognition.stop();
      isListening.value = false;
    }
  }

  return {
    isSupported,
    isListening,
    transcript,
    error,
    start,
    stop,
  };
}
