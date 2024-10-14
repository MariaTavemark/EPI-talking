import threading
import time
import pyttsx3
from AppKit import AVSpeechSynthesizer, AVSpeechSynthesisVoice, AVSpeechUtterance


class TTS:
    def __init__(self, config):
        #Initialize TTS variables
        tts_conf = config['TTS']
        lang = config['Global']['language']
        lang_codes = tts_conf[lang]['lang_codes']

        self.engine_type = tts_conf['type']
        age = tts_conf['age']
        self.volume = float(tts_conf['volume'])

        voice_name = tts_conf[lang][age]["voice_" + self.engine_type]
        self.rate = float(tts_conf[lang][age]["rate_"+ self.engine_type])
        self.pitch = float(tts_conf[lang][age]['pitch_multiplier'])

        if self.engine_type == "pyttsx3":
            self.engine = pyttsx3.init()

            self.engine.setProperty('rate', self.rate) 
            self.engine.setProperty('volume', self.volume)

            voices = list(filter(
                    lambda x: any([True for c in lang_codes if c in x.languages]), 
                    self.engine.getProperty('voices')
                ))

            voice = next((x.id for x in voices if x.name == voice_name), None)
            if voice is None:
                print("Could not find TTS voice", voice_name)
                exit(1)

            self.engine.setProperty('voice', voice) 
            self.tts_thread = None

        elif self.engine_type == "avspeech":
            self.engine = None
            voices_tmp = AVSpeechSynthesisVoice.speechVoices()
            voices = list(filter(lambda x: any([True for c in lang_codes if c in x.language()]), voices_tmp))
            self.voice = next((x for x in voices if x.identifier() == voice_name), None)
            if self.voice is None:
                print("Could not find TTS voice", voice_name)
                exit(1)

                

    def say(self, text: str):
        while (self.isTalking()):
                time.sleep(0.2)

        if self.engine_type == "pyttsx3":
            self.engine.say(text)
            if self.tts_thread:
                self.tts_thread.join()
            self.tts_thread = threading.Thread(target=self.engine.runAndWait())
            self.tts_thread.start()

        elif self.engine_type == "avspeech":
            self.engine = AVSpeechSynthesizer()
            self.engine.setUsesApplicationAudioSession_(False)
            sentence = AVSpeechUtterance()
            sentence.setSpeechString_(text)
            sentence.setRate_(self.rate)
            sentence.setPitchMultiplier_(self.pitch)
            sentence.setVolume_(self.volume)
            sentence.setVoice_(self.voice)
            self.engine.speakUtterance_(sentence)


    def isTalking(self):
        if self.engine_type == "pyttsx3":
            if self.tts_thread:
                return self.tts_thread.is_alive()
            return False
        elif self.engine_type == "avspeech":
            if self.engine:
                return self.engine.isSpeaking()
            return False