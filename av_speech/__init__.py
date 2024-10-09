from .av_speech_synthesis_voice import AVSpeechSynthesisVoice
from .av_speech_synthesis_voice_quality import AVSpeechSynthesisVoiceQuality
from .av_speech_synthesis_voice_gender import AVSpeechSynthesisVoiceGender
from .av_speech_utterance import AVSpeechUtterance
from .av_speech_synthesizer import AVSpeechSynthesizer

__all__ = [
    "AVSpeechSynthesisVoice",
    "AVSpeechSynthesisVoiceQuality",
    "AVSpeechSynthesisVoiceGender",
    "AVSpeechUtterance",
    "AVSpeech",
]


class AVSpeech:
    voice: AVSpeechSynthesisVoice = None

    def __init__(self):
        self._synthesizer = AVSpeechSynthesizer()

    def set_voice(self, voice: AVSpeechSynthesisVoice):
        self.voice = voice

    def say(self, text):
        utterance = AVSpeechUtterance(text, self.voice)
        self._synthesizer.speak_utterance(utterance)