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

#/Users/epi/miniforge3/bin/python3

tts_rate_desired_avspeech = 0.5
tts_rate_desired_avspeech_child = 0.4
tts_pitch = 1.0
tts_pitch_child = 1.7

english = True
swedish = False


en_codes = ["en", "en_GB", "en_US", "en_IN", "en_ZA", "en_IE", "en_AU", "en_GB_U_SD@sd=gbsct"]

def createTTS():
    tts_engine = AVSpeechSynthesizer()
    tts_engine.setUsesApplicationAudioSession_(False)
    return tts_engine

def createSv():
    sentence = "Hej! Jag heter EPI och är en liten söt robot som testar sin röst för att se vilken som passar mig bäst!"
    sentence_sv = AVSpeechUtterance()
    sentence_sv_pitch = AVSpeechUtterance()
    sentence_sv.setSpeechString_(sentence)
    sentence_sv_pitch.setSpeechString_(sentence)
    sentence_sv.setRate_(tts_rate_desired_avspeech)
    sentence_sv.setPitchMultiplier_(tts_pitch)
    sentence_sv_pitch.setRate_(tts_rate_desired_avspeech_child)
    sentence_sv_pitch.setPitchMultiplier_(tts_pitch_child)
    sentence_sv.setVolume_(1.0)
    sentence_sv_pitch.setVolume_(1.0)
    return (sentence_sv, sentence_sv_pitch)

def createEn():
    sentence = "Hello! My name is EPI" # and I am a cute little robot who is testing its voice to see which one suits me the best"
    sentence_en = AVSpeechUtterance()
    sentence_en_pitch = AVSpeechUtterance()
    sentence_en.setSpeechString_(sentence)
    sentence_en_pitch.setSpeechString_(sentence)
    sentence_en.setRate_(tts_rate_desired_avspeech)
    sentence_en.setPitchMultiplier_(tts_pitch)
    sentence_en_pitch.setRate_(tts_rate_desired_avspeech_child)
    sentence_en_pitch.setPitchMultiplier_(tts_pitch_child)
    sentence_en.setVolume_(1.0)
    sentence_en_pitch.setVolume_(1.0)
    return (sentence_en, sentence_en_pitch)

#Pitch is between 0.5 and 2.0
from AppKit import AVSpeechSynthesizer, AVSpeechSynthesisVoice, AVSpeechUtterance
import time
#tts_engine.setOutputChannels_()
voices = AVSpeechSynthesisVoice.speechVoices()

sv_voices = list(filter(lambda x: "sv" in x.language() or "sv-SE" in x.language(), voices))
en_voices = list(filter(lambda x: any([True for c in en_codes if c in x.language()]), voices))
if swedish:
    for i, v in enumerate(sv_voices):
        print("")
        print("Voice", i + 1, "out of", len(sv_voices) + 1)
        print("pitch:", tts_pitch, "rate:", tts_rate_desired_avspeech, str(v)[40:])
        #print(v.identifier())
        tts_engine = createTTS()
        sentence_sv, sentence_sv_pitch = createSv()
        sentence_sv.setVoice_(v)
        sentence_sv_pitch.setVoice_(v)
        print(sentence_sv.volume())
        tts_engine.speakUtterance_(sentence_sv)
        while(tts_engine.isSpeaking()):
            time.sleep(0.2)
        tts_engine = createTTS()
        print("pitch:", tts_pitch_child, "rate:", tts_rate_desired_avspeech_child, str(v)[40:])
        tts_engine.speakUtterance_(sentence_sv_pitch)
        while(tts_engine.isSpeaking()):
            time.sleep(0.2)

if english:
    for i, v in enumerate(en_voices):
        print("")
        print("Voice", i + 1, "out of", len(en_voices) + 1)
        print("pitch:", tts_pitch, "rate:", tts_rate_desired_avspeech, str(v)[40:])
        #print(v.identifier())
        tts_engine = createTTS()
        sentence_en, sentence_en_pitch = createEn()
        sentence_en.setVoice_(v)
        sentence_en_pitch.setVoice_(v)
        tts_engine.speakUtterance_(sentence_en)
        while(tts_engine.isSpeaking()):
            time.sleep(0.2)
        tts_engine = createTTS()
        print("pitch:", tts_pitch_child, "rate:", tts_rate_desired_avspeech_child, str(v)[40:])
        tts_engine.speakUtterance_(sentence_en_pitch)
        while(tts_engine.isSpeaking()):
            time.sleep(0.2)