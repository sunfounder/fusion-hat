from .llm import LLM

class Deepseek(LLM):
    """ Deepseek preset LLM class """
    def __init__(self, *args, **kwargs):
        super().__init__(*args,
            base_url="https://api.deepseek.com",
            **kwargs)

class Grok(LLM):
    """ Grok preset LLM class """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, 
            base_url="https://api.x.ai/v1",
            **kwargs)

class Doubao(LLM):
    """ Doubao preset LLM class """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, 
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            **kwargs)

class Qwen(LLM):
    """ Qwen preset LLM class """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, 
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            **kwargs)

class OpenAI(LLM):
    """ OpenAI preset LLM class """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, 
            base_url="https://api.openai.com/v1",
            **kwargs)

class Ollama(LLM):
    """ Ollama preset LLM class """
    def __init__(self, ip: str="localhost", *args, api_key: str="ollama", **kwargs):
        super().__init__(*args, 
            url=f"http://{ip}:11434/api/chat",
            # base_url=f"http://{ip}:11434/v1",
            api_key=api_key,
            **kwargs)
    
    def add_message(self, role, content, image_path=None):
        """ Add message to messages list

        Args:
            role (str): Role of message, e.g. "user", "assistant"
            content (str): Content of message
            image_path (str, optional): Image path, default is None

        Raises:
            ValueError: Role must be 'user' or 'assistant'
        """
        if role not in ["user", "assistant"]:
            raise ValueError("Role must be 'user' or 'assistant'")

        data = {"role": role, "content": content}
        if image_path is not None:
            # get base64 from image
            base64 = self.get_base64_from_image(image_path)
            # add to content
            data["images"] = [base64]

        self.messages.append(data)

    def decode_stream_response(self, line):
        """ Decode stream response line

        Args:
            line (str): Stream response line

        Returns:
            str: Decoded content, None if error
        """
        import json
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]
        if "error" in data:
            raise Exception(data["error"])
        return None

class Gemini(LLM):
    """ Gemini preset LLM class """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, 
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
            **kwargs)
