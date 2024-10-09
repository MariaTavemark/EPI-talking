from .objc_util import ObjCClass, ObjCInstance

from .av_speech_utterance import AVSpeechUtterance

__all__ = ["AVSpeechSynthesizer"]

_objc_class = ObjCClass("AVSpeechSynthesizer")


class AVSpeechSynthesizer:
    def __init__(self):
        self._synthesizer = _objc_class.new()

    def to_ns(self) -> ObjCInstance:
        return self._synthesizer

    def speak_utterance(self, utterance: AVSpeechUtterance):
        self._synthesizer.speakUtterance_(utterance.to_ns())