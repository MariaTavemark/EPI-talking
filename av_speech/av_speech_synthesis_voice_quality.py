from enum import IntEnum, unique

__all__ = ["AVSpeechSynthesisVoiceQuality"]


@unique
class AVSpeechSynthesisVoiceQuality(IntEnum):
    DEFAULT = 1
    ENHANCED = 2