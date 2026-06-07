import { ref } from "vue";

export function useSpeechRecognition() {
  const isSupported =
    "webkitSpeechRecognition" in window || "SpeechRecognition" in window;
  const isListening = ref(false);
  const transcript = ref("");
  const error = ref(null);

  let recognition = null;
  let accumulatedTranscript = "";

  function start() {
    if (!isSupported) {
      error.value = "您的浏览器不支持语音识别，请使用 Chrome 或 Edge。";
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    accumulatedTranscript = "";

    recognition.onresult = (event) => {
      let interim = "";
      let final = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          final += result[0].transcript;
        } else {
          interim += result[0].transcript;
        }
      }

      if (final) {
        accumulatedTranscript += (accumulatedTranscript ? " " : "") + final.trim();
        transcript.value = accumulatedTranscript;
      } else if (interim) {
        transcript.value = accumulatedTranscript
          ? accumulatedTranscript + " " + interim
          : interim;
      }
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
    return new Promise((resolve) => {
      if (!recognition) {
        resolve("");
        return;
      }

      // Guard: if already stopped, resolve immediately
      const originalOnEnd = recognition.onend;
      recognition.onend = () => {
        isListening.value = false;
        if (originalOnEnd && originalOnEnd !== recognition.onend) {
          originalOnEnd();
        }
        // Give a microtask for the final onresult to settle
        setTimeout(() => resolve(transcript.value), 0);
      };

      recognition.stop();
    });
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
