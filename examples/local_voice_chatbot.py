import re
import time
from fusion_hat.llm import Ollama
from fusion_hat.stt import Vosk
from fusion_hat.tts import Piper

# Initialize speech recognition
stt = Vosk(language="en-us")

# Initialize TTS
tts = Piper()
tts.set_model("en_US-amy-low")

# Instructions for the LLM
INSTRUCTIONS = (
    "You are a helpful assistant. Answer directly in plain English. "
    "Do NOT include any hidden thinking, analysis, or tags like <think>."
)
WELCOME = "Hello! I'm your voice chatbot. Speak when you're ready."

# Initialize Ollama connection
llm = Ollama(ip="localhost", model="llama3.2:3b")
llm.set_max_messages(20)
llm.set_instructions(INSTRUCTIONS)

# Utility: clean hidden reasoning
def strip_thinking(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<\s*think[^>]*>.*?<\s*/\s*think\s*>", "", text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r"<\s*thinking[^>]*>.*?<\s*/\s*thinking\s*>", "", text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r"```(?:\s*thinking)?\s*.*?```", "", text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r"\[/?thinking\]", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+\n", "\n", text).strip()

def main():
    print(WELCOME)
    tts.say(WELCOME)

    try:
        while True:
            print("\n🎤 Listening... (Press Ctrl+C to stop)")

            # Collect final transcript from Vosk
            text = ""
            for result in stt.listen(stream=True):
                if result["done"]:
                    text = result["final"].strip()
                    print(f"[YOU] {text}")
                else:
                    print(f"[YOU] {result['partial']}", end="\r", flush=True)

            if not text:
                print("[INFO] Nothing recognized. Try again.")
                time.sleep(0.1)
                continue

            # Query Ollama with streaming
            reply_accum = ""
            response = llm.prompt(text, stream=True)
            for next_word in response:
                if next_word:
                    print(next_word, end="", flush=True)
                    reply_accum += next_word
            print("")

            # Clean and speak
            clean = strip_thinking(reply_accum)
            if clean:
                tts.say(clean)
            else:
                tts.say("Sorry, I didn't catch that.")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n[INFO] Stopping...")
    finally:
        tts.say("Goodbye!")
        print("Bye.")

if __name__ == "__main__":
    main()