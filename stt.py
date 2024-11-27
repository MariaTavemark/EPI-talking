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

import vosk
import queue
import json
import sounddevice

class STT:
    def __init__(self, config):
        stt_conf = config["STT"]
        lang = config["Global"]["language"]

        self.q = queue.Queue()

        device = sounddevice.query_devices(kind='input')
        sample_rate = int(device["default_samplerate"])
        chunk_size = int(stt_conf["chunk_size"])
        model_name = stt_conf[lang]["model"]

        model = vosk.Model(model_name) 
        self.engine = vosk.KaldiRecognizer(model, sample_rate)

        self.paused = True

        self.stream = sounddevice.RawInputStream(
                    samplerate=sample_rate,
                    blocksize = chunk_size,
                    device=device['index'],
                    dtype="int16", channels=1, 
                    callback=self.audio_add
                    )
        self.stream.start()
        

    # Method that is called whenever the audio stream gets data. Put audio in queue to be processed.
    def audio_add(self, indata, frames, time, status):
        if status:
            print("STT capture had status: ", status)
        if not self.paused:
            self.q.put(bytes(indata))

    
    def recognize(self):
        if self.q.empty():
            return None
        data = self.q.get()
        # If stt recognizes data as speech
        if self.engine.AcceptWaveform(data):
            res = self.engine.Result()
            result = json.loads(res)
            recognized_text = result['text']
            return recognized_text
        else:
            return None
        

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
    