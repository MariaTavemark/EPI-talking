from .av_speech_synthesis_voice import AVSpeechSynthesisVoice
from .av_speech_synthesis_voice_quality import AVSpeechSynthesisVoiceQuality
from .av_speech_synthesis_voice_gender import AVSpeechSynthesisVoiceGender
from .av_speech_utterance import AVSpeechUtterance
from .av_speech_synthesizer import AVSpeechSynthesizer
from .objc_util import ObjCBlock, ObjCClass, ObjCClassMethod, ObjCClassMethodProxy, ObjCInstance, ObjCInstanceMethod, ObjCInstanceMethodProxy, ObjCIterator
from .objc_util import CGAffineTransform, CGPoint, CGRect, CGSize, CGVector, UIEdgeInsets, NSRange, objc_method_description, _block_descriptor

__all__ = [
    "AVSpeechSynthesisVoice",
    "AVSpeechSynthesisVoiceQuality",
    "AVSpeechSynthesisVoiceGender",
    "AVSpeechUtterance",
    "AVSpeech",
    "ObjCBlock",
    "ObjCClass",
    "ObjCClassMethod",
    "ObjCClassMethodProxy",
    "ObjCInstance",
    "ObjCInstanceMethod",
    "ObjCInstanceMethodProxy",
    "ObjCIterator",
    "CGAffineTransform",
    "CGPoint",
    "CGRect",
    "CGSize",
    "CGVector",
    "UIEdgeInsets",
    "NSRange",
    "objc_method_description",
    "_block_descriptor",
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