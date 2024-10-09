from typing import Optional

from objc_util import ObjCClass, ObjCInstance

from .av_speech_synthesis_voice import AVSpeechSynthesisVoice

__all__ = ["AVSpeechUtterance"]

_objc_class = ObjCClass("AVSpeechUtterance")


class AVSpeechUtterance:
    def __init__(
        self,
        speech_string: str,
        voice: Optional[AVSpeechSynthesisVoice] = None,
        rate: Optional[float] = None,
        volume: Optional[float] = None,
        pitch_multiplier: Optional[float] = None,
        pre_utterance_delay: Optional[float] = None,
        post_utterance_delay: Optional[float] = None,
    ):
        """"A chunk of text to be spoken, along with parameters that affect its speech.
        :param speech_string:
        :param voice:
        :param rate:
        :param volume:
        :param pitch_multiplier:
        :param pre_utterance_delay:
        :param post_utterance_delay:
        """
        self._speech_string: str = speech_string
        self.voice: AVSpeechSynthesisVoice = voice
        self.rate: float = rate
        self.volume: float = volume
        self.pitch_multiplier: float = pitch_multiplier
        self.pre_utterance_delay: float = pre_utterance_delay
        self.post_utterance_delay: float = post_utterance_delay

    @property
    def speech_string(self) -> str:
        """The text to be spoken in the utterance. (read only)
        """
        return self._speech_string

    @classmethod
    def from_speech_string(cls, speech_string: str) -> "AVSpeechUtterance":
        data = _objc_class.speechUtteranceWithString_(speech_string)
        return cls(
            speech_string,
            voice=None,
            rate=data.rate(),
            volume=data.volume(),
            pitch_multiplier=data.pitchMultiplier(),
            pre_utterance_delay=data.preUtteranceDelay(),
            post_utterance_delay=data.postUtteranceDelay(),
        )

    def to_ns(self) -> ObjCInstance:
        data = _objc_class.speechUtteranceWithString_(self.speech_string)

        if self.voice is not None:
            data.voice = self.voice.to_ns()
        if self.rate is not None:
            data.rate = self.rate
        if self.volume is not None:
            data.volume = self.volume
        if self.pitch_multiplier is not None:
            data.pitchMultiplier = self.pitch_multiplier
        if self.pre_utterance_delay is not None:
            data.preUtteranceDelay = self.pre_utterance_delay
        if self.post_utterance_delay is not None:
            data.postUtteranceDelay = self.post_utterance_delay

        return data

    def __repr__(self):
        # TODO: DRY
        if self.voice:
            return (
                f"<{self.__class__.__name__!r}: String: {self.speech_string}\n"
                f"Voice: {self.voice.name} ({self.voice.language})\n"
                f"Rate: {self.rate}\n"
                f"Volume: {self.volume}\n"
                f"Pitch Multiplier: {self.pitch_multiplier}"
                f"Delays: Pre: {self.pre_utterance_delay}(s) Post: {self.post_utterance_delay}(s)>"
            )
        else:
            return (
                f"<{self.__class__.__name__!r}: String: {self.speech_string}\n"
                f"Voice: (none)\n"
                f"Rate: {self.rate}\n"
                f"Volume: {self.volume}\n"
                f"Pitch Multiplier: {self.pitch_multiplier}"
                f"Delays: Pre: {self.pre_utterance_delay}(s) Post: {self.post_utterance_delay}(s)>"
            )