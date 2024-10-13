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
    