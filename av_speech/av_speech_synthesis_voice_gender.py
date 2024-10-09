from enum import IntEnum, unique

__all__ = ["AVSpeechSynthesisVoiceGender"]


@unique
class AVSpeechSynthesisVoiceGender(IntEnum):
    FEMALE = 1
    MALE = 2
    UNKNOWN = 3