from typing import List, Optional

from objc_util import ObjCClass, ObjCInstance

from .av_speech_synthesis_voice_quality import AVSpeechSynthesisVoiceQuality
from .av_speech_synthesis_voice_gender import AVSpeechSynthesisVoiceGender
from .utils import ns_string_to_py_string

__all__ = ["AVSpeechSynthesisVoice"]

_objc_class = ObjCClass("AVSpeechSynthesisVoice")


class AVSpeechSynthesisVoice:
    def __init__(
        self, language: str, identifier: str, name: str, quality: int, gender: int
    ) -> None:
        """A distinct voice for use in speech synthesis.
        (Implements AVFoundation's AVSpeechSynthesisVoice)
        :param language: A BCP 47 code identifying the voice’s language and locale.
        :type language: str
        :param identifier: The unique identifier for a voice object.
        :type identifier: str
        :param name: The name for a voice object.
        :type: name: str
        :param quality: The speech quality for a voice object.
        :type quality: int
        :param gender: The gender of the voice
        :type gender: int
        """
        self.language: str = language
        self.identifier: str = identifier
        self.name: str = name
        self.quality: AVSpeechSynthesisVoiceQuality = AVSpeechSynthesisVoiceQuality(
            quality
        )
        self.gender: AVSpeechSynthesisVoiceGender = AVSpeechSynthesisVoiceGender(gender)

    @property
    def current_language_code(self) -> str:
        """Returns the code for the user’s current locale.
        :return: A string containing the BCP 47 language and locale code for
        the user’s current locale.
        """
        return ns_string_to_py_string(_objc_class.currentLanguageCode())

    @classmethod
    def get_speech_voices(cls) -> List["AVSpeechSynthesisVoice"]:
        """Returns all available voices.
        :return: A list of all available voices as AVSpeechSynthesisVoice
        """
        voices = _objc_class.speechVoices()
        data = []
        for voice in voices:
            data.append(
                cls(
                    ns_string_to_py_string(voice.language()),
                    ns_string_to_py_string(voice.identifier()),
                    ns_string_to_py_string(voice.name()),
                    voice.quality(),
                    voice.gender(),
                )
            )
        return data

    @classmethod
    def voice_with_identifier(
        cls, identifier: str
    ) -> Optional["AVSpeechSynthesisVoice"]:
        """Returns a voice object for the specified identifier.
        :param identifier: The unique identifier for a voice.
        :type identifier: str
        :return: The voice object for the requested identifier,
        or `None` if the identifier is invalid or isn't available on the device.
        """
        voice = _objc_class.voiceWithIdentifier_(identifier)

        if not voice:
            # Voice not found or not available
            return None

        return cls(
            ns_string_to_py_string(voice.language()),
            ns_string_to_py_string(voice.identifier()),
            ns_string_to_py_string(voice.name()),
            voice.quality(),
            voice.gender(),
        )

    @classmethod
    def voice_with_language(
        cls, language: str, gender: Optional[AVSpeechSynthesisVoiceGender] = None
    ) -> Optional["AVSpeechSynthesisVoice"]:
        """Returns a voice object for the specified language and locale.
        :param language: A BCP 47 code specifying language and locale for a voice.
        :type language: str
        :param gender: Optional gender to match with the voice
        :type: gender: AVSpeechSynthesisVoiceGender or `None`
        :return: The voice object for the requested language as AVSpeechSynthesisVoice,
        or `None` if the language references a locale/language for which no voice exists.
        """
        if not gender:
            voice = _objc_class.voiceWithLanguage_(language)

            if not voice:
                # No voice available for input
                return None

            return cls(
                ns_string_to_py_string(voice.language()),
                ns_string_to_py_string(voice.identifier()),
                ns_string_to_py_string(voice.name()),
                voice.quality(),
                voice.gender(),
            )
        else:
            voices = cls.get_speech_voices()

            for voice in voices:
                if voice.language == language and voice.gender == gender:
                    return voice
            else:
                return None

    def to_ns(self) -> ObjCInstance:
        """Make the original class available for usage in objc_utils code.
        :return: This voice as AVSpeechSynthesisVoice ObjCInstance
        """
        return _objc_class.voiceWithIdentifier_(self.identifier)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__!r}: Language: {self.language}, Name: {self.name}, "
            f"Gender: {self.gender} Quality: {self.quality} [{self.identifier}]>"
        )