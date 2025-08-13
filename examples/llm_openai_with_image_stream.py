from fusion_hat.llm import LLM
from picamera2 import Picamera2
import time

from secret import OPENAI_API_KEY

INSTRUCTIONS = "You are a funny rejector, who will reject any question or request with a funny reason."
WELCOME = "Ask me anything, maybe I can help. (or not)"

llm = LLM(api_key=OPENAI_API_KEY)
llm.set_model("gpt-4o")
# Set how many messages to keep
llm.set_max_messages(20)
# Set instructions
llm.set_instructions(INSTRUCTIONS)
# Set welcome message
llm.set_welcome(WELCOME)

# Init camera
camera = Picamera2()
config = camera.create_still_configuration()
camera.configure(config)
camera.start()
time.sleep(2)

print(WELCOME)

while True:
    # Wait for user input
    input_text = input(">>> ")

    # Capture image
    img_path = '/tmp/fusion-hat-llm-img.jpg'
    camera.capture_file(img_path)

    # Prompt with image
    response = llm.prompt(input_text, image_path=img_path, stream=True)

    for next_word in response:
        if next_word:
            print(next_word, end="", flush=True)
    print("")

