__all__ = [
    "VoiceAssistant"
]
from sunfounder_voice_assistant.voice_assistant import VoiceAssistant
from .device import enable_speaker

__original_init__ = VoiceAssistant.__init__
def __new_init__(self, *args, **kwargs):
    __original_init__(self, *args, **kwargs)
    enable_speaker()
VoiceAssistant.__init__ = __new_init__
