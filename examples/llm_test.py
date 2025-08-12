from fusion_hat.llm import LLM

INSTRUCTIONS = "You are a funny rejector, who will reject any question or request with a funny reason."
WELCOME = "Ask me anything, maybe I can help. (or not)"

llm = LLM()
# Set Deepseek V3
# llm.set_base_url("https://api.deepseek.com")
# llm.set_model("deepseek-chat")

# Set Deepseek R1
# llm.set_base_url("https://api.deepseek.com")
# llm.set_model("deepseek-reasoner")

# Set OpenAI gpt4o
llm.set_model("gpt-4o")

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

