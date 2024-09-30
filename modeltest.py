#/Users/epi/miniforge3/bin/python3

# LLM:
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM


#STT:
import vosk
#import pyaudio
import queue
import json
import sounddevice

#TTS:
import pyttsx3

#Initialize TTS variables
tts_engine = pyttsx3.init()

tts_rate = tts_engine.getProperty('rate') 
print("Default speaking rate is:", tts_rate)
#Mess with the below to change rate of speech
tts_rate_desired = 125
tts_engine.setProperty('rate', tts_rate_desired) 
print("Our speaking rate is:", tts_rate_desired)

tts_volume = tts_engine.getProperty('volume')
print("Default tts volume is:", tts_volume)
#Change below to change volume (0.0-1.0)
tts_volume_desired = 1.0
tts_engine.setProperty('volume',tts_volume_desired)
print("Our tts volume is:", tts_volume_desired)

tts_voices = tts_engine.getProperty('voices') 
print("Available tts voices: 0 to ", len(tts_voices) - 1)
# Change below value to something that was printed by the row above...
tts_voice = 0 # Ok voices seem to be 88(male), 69(female), 2, 3, 13
#Funny values on the above (robotic/strange): 40, 61, 87, 113, 118, 139, 140, 144
tts_engine.setProperty('voice', tts_voices[tts_voice].id) 
print("Our tts voice choice is:", tts_voice)



#Initialize STT variables
stt_queue = queue.Queue()

stt_device = sounddevice.query_devices(kind='input')
stt_sample_rate = int(stt_device["default_samplerate"])

stt_model_name= "vosk-model-small-sv-rhasspy-0.15"
stt_model = vosk.Model(stt_model_name)
stt_chunk_size = 8000 #4096
stt = vosk.KaldiRecognizer(stt_model, stt_sample_rate)

def stt_audio_add(indata, frames, time, status):
    #print("STT CALLBACK")
    if status:
        print("STT capture had status: ", status)
    stt_queue.put(bytes(indata))

stream = sounddevice.RawInputStream(samplerate=stt_sample_rate, blocksize = stt_chunk_size, device=stt_device['index'],
            dtype="int16", channels=1, callback=stt_audio_add)
#print(stream.active)
#stream.start()
#print(stream.active)


# Initialize LLM Variables
llm_name = "AI-Sweden-Models/gpt-sw3-6.7b-v2"
#llm_name = "AI-Sweden-Models/gpt-sw3-1.3b"
#llm_name = "AI-Sweden-Models/gpt-sw3-356m" # Fungerar, är bara lite dum
#llm_name = "AI-Sweden-Models/gpt-sw3-6.7b-v2-instruct-4bit-gptq"
llm_device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Initialize Tokenizer & Model
llm_tokenizer = AutoTokenizer.from_pretrained(llm_name, use_fast=False)
llm_model = AutoModelForCausalLM.from_pretrained(llm_name, low_cpu_mem_usage=False)
llm_model.eval()
llm_model.to(llm_device)


llm_base_prompt = """
Du är EPI, en gullig robot som ska prata med sina vänner och känna igen dem. Du kan visa känslor, men ska 
generellt sett vara glad och snäll. Du får aldrig diskriminera någon. Din kompis, en användare, har sagt något till dig. 
Besvara dem, och agera som den snälla roboten som heter EPI.

Användaren sade: 
"""

#Metod som ger svar baserat på en prompt/fråga
def generate_answer(prompt):
    #["input_ids"]
    input_ids = llm_tokenizer(llm_base_prompt + prompt, return_tensors="pt")["input_ids"].to(llm_device)
    #print("Generated input_ids")
    generated_token_ids = llm_model.generate(
        inputs=input_ids,
        max_new_tokens=100,
        #max_length=30,
        do_sample=False,
        #temperature=0.6,
        top_p=1,
    )[0]
    #print("Generated token_ids")

    generated_text = llm_tokenizer.decode(generated_token_ids, skip_special_tokens=True)  
    
    return generated_text


def stt_recognize():
    data = stt_queue.get()
    #print("Am I here?")
    # If stt recognizes data as speech
    if stt.AcceptWaveform(data):
        res = stt.Result()
        result = json.loads(res)
        recognized_text = result['text']
        #print(res)
        return recognized_text
    else:
        #print("STT was not sure, but thought it heard: ", stt.PartialResult())
        # No speech detected in audio. If persistant problem, try messing with stt_chunk_size
        return None




# EXEMPEL för LLM:
prompt = "Hej, jag heter Maria. Vad heter du?"
print("Generating answer for prompt: ", prompt)
print(generate_answer(prompt))  

#print("Listening...")

# EXEMPEL för STT:
#recognized_audio = stt_recognize()

# EXEMPEL för TTS:
#tts_engine.say("Hej, detta är ett test!")
#tts_engine.say('Jag pratar i hastigheten ' + str(tts_rate_desired))
#tts_engine.runAndWait()

#OBS OBS OBS kommentera bort exempel ovan innan nedan ska köras

def run_stt_to_llm():
    stream.start()
    while True:
        result = stt_recognize()
        #Test if we recognized any speech
        if result:
            print("Recognized text was:", result)
            #Pass to LLM
            #answer = generate_answer(result)
            #print("Answer was:", answer)
            #Pass to TTS
            stream.stop()
            #tts_engine.say(answer)
            tts_engine.say(result)
            tts_engine.runAndWait()
            stream.start()

            #Add epi-moves and stuff in this method
        else:
            #Maybe make epi do something if it did not recognize any speech (pass below means "do nothing")
            pass

if __name__ == "__main__":
    try:
        run_stt_to_llm()
    except KeyboardInterrupt as k:
        print("Goodbye!")
    finally:
        exit(0)


#run with "python3 modeltest.py"