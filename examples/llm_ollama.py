from fusion_hat.llm import Ollama
'''
You can run llm locally! with ollama

Option 1. Run Ollama on your Pi or an Linux PC

    ```bash
    # Install Ollama
    curl -fsSL https://ollama.com/install.sh | sh
    # Pull model: llama3.2:3b
    ollama pull llama3.2:3b
    # Try to run model:
    ollama run llama3.2:3b
    # If it work, then we can serve it
    ollama serve
    ```

Option 2. Run Ollama on your Mac or Windows

    1. go to https://ollama.com/download download and install ollama
    2. Open Ollama application, You can see a chatting window. click on the model selection, in Find Models, type in llama3.2:3b, we try a small model first.
    3. You can see the model in the list, click on it. Then say something, like just a Hi. The model will download automatically.
    4. Do not click anywhere else, and just stay on this window and wait until the download finished.
    5. After downloaded, you should get a proper response from llama3.2:3b, you can chat with it a little bit, and we move on.
    6. Click Settings on the left, and enable "Expose Ollama to the network", this allow your PiCar-X to access.
    7. Go back and now it's ready.

Warning:
    If you get error like: "Error: 500 Internal Server Error: model requires more system memory (5.1 GiB) than is available (3.7 GiB)"
    It is because the model you choose is to large for you computer. try a better computer or a smaller model.
'''

INSTRUCTIONS = "You are a helpful assistant."
WELCOME = "Hello, I am a helpful assistant. How can I help you?"

# Change this to your computer IP, if you run it on your pi, then change it to localhost
llm = Ollama(
    ip="localhost",          # e.g., "192.168.100.145" if remote
    model="llama3.2:3b"
)

# Set how many messages to keep
llm.set_max_messages(20)
# Set instructions
llm.set_instructions(INSTRUCTIONS)
# Set welcome message
llm.set_welcome(WELCOME)

print(WELCOME)

while True:
    input_text = input(">>> ")

    # Response without stream
    # response = llm.prompt(input_text)
    # print(f"response: {response}")

    # Response with stream
    response = llm.prompt(input_text, stream=True)
    for next_word in response:
        if next_word:
            print(next_word, end="", flush=True)
    print("")
