#EPI-Talking
#Copyright (C) 2024  Maria Tavemark
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.
#
#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
from random import random
import time
from AppKit import AVSpeechSynthesizer, AVSpeechSynthesisVoice, AVSpeechUtterance


class TTS:
    def __init__(self, config):
        #Initialize TTS variables
        tts_conf = config['TTS']
        lang = config['Global']['language']
        self.lang_codes = tts_conf[lang]['lang_codes']
        self.volume = float(tts_conf['volume'])
        self.engine = None

        self.names = tts_conf[lang]["names"]
        self.rates = tts_conf[lang]["rates"]
        self.pitches = tts_conf[lang]["pitches"]
        self.voices = tts_conf[lang]["voices"]

        self.used_voices = []
        self.max_index = min(len(self.names), len(self.rates), len(self.pitches), len(self.voices)) - 1

        self.doing_summary = False

        self.next_voice()



    def create_engine(self):
        voices_tmp = AVSpeechSynthesisVoice.speechVoices()
        voices = list(filter(lambda x: any([True for c in self.lang_codes if c in x.language()]), voices_tmp))
        self.voice = next((x for x in voices if x.identifier() == self.voice_name), None)
        if self.voice is None:
            print("TTS - Could not find TTS voice", self.voice_name)
            exit(1)

        print("TTS - Now using " + self.name + " " + self.get_progress())


    def next_voice(self):
        next_index = round(random() * self.max_index)
        if len(self.used_voices) == len(self.voices):
            print("TTS - You have now used all voices and lines on this test person.")
            return "Done"
        while (next_index in self.used_voices):
            next_index = round(random() * self.max_index)

        self.used_voices.append(next_index)

        self.name = self.names[next_index]
        self.rate = float(self.rates[next_index])
        self.pitch = float(self.pitches[next_index])
        #print(self.pitch)
        #print(self.rate)
        self.voice_name = self.voices[next_index]

        self.create_engine()


    def summary(self, line):
        self.doing_summary = True
        for i in self.used_voices:
            self.summary_step(line, i)
        self.doing_summary = False


    def summary_step(self, line, i):
        self.name = self.names[i]
        self.rate = float(self.rates[i])
        self.pitch = float(self.pitches[i])
        self.voice_name = self.voices[i]

        self.create_engine()
        self.say(line)
        while(self.isTalking()):
            time.sleep(0.2)
        time.sleep(1)


    def get_progress(self):
        if self.doing_summary:
            return ""
        return "(" + str(len(self.used_voices)) + "/" + str((self.max_index + 1)) + ")"

    def say(self, text: str):
        while (self.isTalking()):
                time.sleep(0.2)

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
        if self.engine:
            return self.engine.isSpeaking()
        return False