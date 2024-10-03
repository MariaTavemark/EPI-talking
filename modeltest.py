#/Users/epi/miniforge3/bin/python3

#LLM key file choosing
from random import random
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os.path

# LLM:
from openai import OpenAI
import json
import openai


#STT:
import vosk
import queue
import json
import sounddevice

#TTS:
import pyttsx3
import threading

#EPI:
import requests

debug = False


#LLM key file config
default_keyfile = "/Volumes/MARIAT/openai.txt"
try:
    if not os.path.isfile(default_keyfile):
        print("Please select the key-file")
        Tk().withdraw()
        keyfile_path = askopenfilename()
    else:
        keyfile_path = default_keyfile
    keyfile = open(keyfile_path, 'r')
    llm_org, llm_proj, llm_api_key = [k.removesuffix("\n") for k in keyfile.readlines()]
except Exception as err:
    print("There was an error when opening the key-file. Shutting down.", err)
    exit(1)







#Initialize TTS variables
#Change below to change volume (0.0-1.0)
tts_volume_desired = 1.0
#Mess with the below to change rate of speech
tts_rate_desired = 125

tts_voice = 69 # Ok voices seem to be 88(male), 69(female), 2, 3, 13
#Funny values on the above (robotic/strange): 40, 61, 87, 113, 118, 139, 140, 144  (87 is scary and singing!!)

tts_engine = pyttsx3.init()

tts_rate = tts_engine.getProperty('rate') 
print("Default speaking rate is:", tts_rate)
tts_engine.setProperty('rate', tts_rate_desired) 
print("Our speaking rate is:", tts_rate_desired)

tts_volume = tts_engine.getProperty('volume')
print("Default tts volume is:", tts_volume)
tts_engine.setProperty('volume',tts_volume_desired)
print("Our tts volume is:", tts_volume_desired)

"sv"
"sv_SE"
tts_voices = list(filter(lambda x: 'sv' in x.languages, tts_engine.getProperty('voices')))
if len(tts_voices) == 0:
    tts_voices = tts_engine.getProperty('voices')
print("Available tts voices: 0 to ", len(tts_voices) - 1)
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

# Method that is called whenever the audio stream gets data. Put audio in queue to be processed.
def stt_audio_add(indata, frames, time, status):
    if status:
        print("STT capture had status: ", status)
    stt_queue.put(bytes(indata))

stream = sounddevice.RawInputStream(samplerate=stt_sample_rate, blocksize = stt_chunk_size, device=stt_device['index'],
            dtype="int16", channels=1, callback=stt_audio_add)




# Initialize EPI-head variables
epi_url = "http://127.0.0.1:8000"
epi_control_path = "/control/SR.positions/"

epi_channels = {
    "neck_tilt": 0,
    "neck_pan": 1,
    "left_eye": 2,
    "right_eye": 3,
    "left_pupil": 4,
    "right_pupil": 5,
    "eyes_r": 19,
    "eyes_g": 20,
    "eyes_b": 21,
    "eyes_intensity": 22,
    "mouth_r": 23,
    "mouth_g": 24,
    "mouth_b": 25,
    "mouth_intensity": 26,
    "sound_clip": 27
}

epi_valid_ranges = {
    "neck_tilt": (-55, 55),
    "neck_pan": (-30, 30),
    "left_eye": (-20, 20),
    "right_eye": (-20, 20),
    "left_pupil": (0, 100),
    "right_pupil": (0, 100),
    "eyes_r": (0, 100),
    "eyes_g": (0, 100),
    "eyes_b": (0, 100),
    "eyes_intensity": (0.0, 1.0),
    "mouth_r": (0, 100),
    "mouth_g": (0, 100),
    "mouth_b": (0, 100),
    "mouth_intensity": (0.0, 1.0),
    "sound_clip": 27
}



# Initialize LLM Variables
llm_model="gpt-4o-mini"

#How random the answers should be [0.0-2.0]
llm_temperature = 0.8

llm_client = OpenAI(
    organization=llm_org,
    project=llm_proj,
    api_key=llm_api_key
)

#Just for fun
llm_input_token_count = 0
llm_output_token_count = 0

llm_input_token_cost = {
    "gpt-4o-mini": 0.000001545,
    "gpt-4o-mini-2024-07-18": 0.000001545,
    "gpt-4o-2024-08-06": 0.00002575,
    "gpt-4o-2024-05-13": 0.0000515,
    "gpt-4o": 0.0000515,
    "o1-mini": 0.0000309,
    "o1-mini-2024-09-12": 0.0000309,
    "o1-preview": 0.0001545,
    "o1-preview-2024-09-12": 0.0001545,
}

llm_output_token_cost = {
    "gpt-4o-mini": 0.00000618,
    "gpt-4o-mini-2024-07-18": 0.00000618,
    "gpt-4o-2024-08-06": 0.000103,
    "gpt-4o-2024-05-13": 0.0001545,
    "gpt-4o": 0.0001545,
    "o1-mini": 0.0001236,
    "o1-mini-2024-09-12": 0.0001236,
    "o1-preview": 0.000618,
    "o1-preview-2024-09-12": 0.000618,
}

llm_instructions = {"role": "system", "content": """
Du är EPI, en gullig robot som ska prata med sina vänner och känna igen dem. Du kan visa känslor, men ska 
generellt sett vara glad och snäll. Du får aldrig diskriminera någon. Användaren kan inte säga ditt namn på grund av dålig taligenkänning, så
om användaren verkar kalla dig något annat namn ska du ignorera det och fortsätta som vanligt. Använd inte några specialtecken i dina svar, utan bara a till ö och skiljetecken.
Avsluta ditt svar med att skriva en av följande fraser, baserat på hur EPI känner sig: arg, glad, ledsen, neutral
"""}

llm_message_history = [llm_instructions]

#Metod som ger svar baserat på en prompt/fråga
def generate_answer(prompt):
    global llm_input_token_count
    global llm_output_token_count

    message = {"role": "user", "content": prompt}
    llm_message_history.append(message)
    out = llm_client.chat.completions.create(
        model=llm_model,
        messages=llm_message_history,
        temperature=llm_temperature,
        n=1,
        max_completion_tokens=1000,
        timeout=10
    )

    reply = out.choices[0].message.content
    role = out.choices[0].message.role
    llm_message_history.append({"role": role, "content": reply})

    llm_input_token_count += out.usage.prompt_tokens
    llm_output_token_count += out.usage.completion_tokens
    
    return reply


def stt_recognize():
    if stt_queue.empty():
        return None
    data = stt_queue.get()
    # If stt recognizes data as speech
    if stt.AcceptWaveform(data):
        res = stt.Result()
        result = json.loads(res)
        recognized_text = result['text']
        return recognized_text
    else:
        #print("STT was not sure, but thought it heard: ", stt.PartialResult())
        # No speech detected in audio. If persistant problem, try messing with stt_chunk_size
        return None
    

def control_epi(channel, value):
    if channel not in epi_channels:
        raise ValueError("Invalid EPI channel sent:", channel)
    valid_values = epi_valid_ranges[channel]
    if valid_values[0] <= value <= valid_values[1]:
         requests.get(epi_url + epi_control_path + str(epi_channels[channel]) + "/0/" + str(value), timeout=0.1)



#Creat epi moods below


def epi_neutral():
    control_epi("mouth_intensity", 0.5)
    control_epi("mouth_r", 50)
    control_epi("mouth_g", 50)
    control_epi("mouth_b", 0)
    control_epi("eyes_r", 50)
    control_epi("eyes_g", 50)
    control_epi("eyes_b", 0)
    control_epi("eyes_intensity", 0.2)
    control_epi("left_pupil", 20)
    control_epi("right_pupil", 20)

def epi_sad():
    control_epi("mouth_intensity", 0.2)
    control_epi("mouth_r", 0)
    control_epi("mouth_g", 0)
    control_epi("mouth_b", 100)
    control_epi("eyes_r", 0)
    control_epi("eyes_g", 0)
    control_epi("eyes_b", 100)
    control_epi("eyes_intensity", 0.2)
    control_epi("left_pupil", 100)
    control_epi("right_pupil", 100)

def epi_happy():
    control_epi("mouth_intensity", 0.5)
    control_epi("mouth_r", 0)
    control_epi("mouth_g", 100)
    control_epi("mouth_b", 0)
    control_epi("eyes_r", 0)
    control_epi("eyes_g", 100)
    control_epi("eyes_b", 0)
    control_epi("eyes_intensity", 0.5)
    control_epi("left_pupil", 50)
    control_epi("right_pupil", 50)

def epi_angry():
    control_epi("mouth_intensity", 1.0)
    control_epi("mouth_r", 100)
    control_epi("mouth_g", 0)
    control_epi("mouth_b", 0)
    control_epi("eyes_r", 100)
    control_epi("eyes_g", 0)
    control_epi("eyes_b", 0)
    control_epi("eyes_intensity", 1.0)
    control_epi("left_pupil", 0)
    control_epi("right_pupil", 0)

def epi_shake_head():
    num_shakes = 2
    degrees = 20
    delay = 0.02

    for i in range(num_shakes):
        for j in range(-degrees, degrees):
            control_epi("neck_pan", j)
            time.sleep(delay)

    control_epi("neck_pan", 0)

def epi_nod():
    num_shakes = 2
    min_degrees = 0
    max_degrees = 15
    delay = 0.02

    for i in range(num_shakes):
        for j in range(min_degrees, max_degrees):
            control_epi("neck_tilt", j)
            time.sleep(delay)

    control_epi("neck_tilt", 0)


def epi_thinking():
    control_epi("left_pupil", 50)
    control_epi("right_pupil", 50)


def epi_done_thinking():
    control_epi("left_pupil", 20)
    control_epi("right_pupil", 20)


def newTTSthread():
    return threading.Thread(target=tts_engine.runAndWait())


def run_stt_to_llm():
    print("System ready")
    print("EPI is angry")
    epi_angry()
    time.sleep(1)
    print("EPI is sad")
    epi_sad()
    time.sleep(1)
    print("EPI is happy")
    epi_happy()
    time.sleep(1)
    print("EPI is neutral")
    epi_neutral()
    time.sleep(1)
    print("EPI is saying no")
    epi_shake_head()
    time.sleep(1)
    print("EPI is saying yes")
    epi_nod()

    tts_thread:threading.Thread = newTTSthread()

    stream.start()
    tts_engine.say("Hej!")
    tts_thread.start()
    while tts_thread.is_alive():
        time.sleep(0.1)

    print("EPI is listening")


    while True:
        result = stt_recognize()
        #Test if we recognized any speech
        if result:
            if debug: print("Recognized text was:", result)
            print("You said:", result)
            #Pass to LLM
            #epi_thinking()
            print("EPI is thinking....")
            answer = generate_answer(result).split()
            if debug: print("Answer was:", answer)
            #epi_done_thinking()

            #Pass to TTS
            stream.stop()


            print("EPI is talking")
            print("EPI said: ", " ".join(answer[:-1]))
            mood:str = answer[-1:][0]

            if "glad" in mood.lower():
                print("EPI is happy")
                epi_happy()
            elif "arg" in mood.lower():
                print("EPI is angry")
                epi_angry()
            elif "ledsen" in mood.lower():
                print("EPI is sad")
                epi_sad()
            else:
                print("Epi had the mood", mood.lower())
                epi_neutral()

            if "nej" in answer[:-1] or "Nej" in answer[:-1]:
                epi_shake_head()
            elif "ja" in answer[:-1] or "Ja" in answer[:-1]:
                epi_nod()

            tts_engine.say(" ".join(answer[:-1]))
            tts_thread = newTTSthread()
            tts_thread.start()

            #print("EPI is talking and flashing")
            while tts_thread.is_alive():
                intensity = random()
                #print("Random mouth intensity: ", intensity)
                control_epi("mouth_intensity", intensity)
                time.sleep(0.5)

            epi_neutral()
            stream.start()
            print("EPI is listening")
            
            

            #Add epi-moves and stuff in this method
        else:
            #Maybe make epi do something if it did not recognize any speech (pass below means "do nothing")
            pass

if __name__ == "__main__":
    try:
        for _ in range(100):
            print()
        run_stt_to_llm()
    except KeyboardInterrupt as k:
        print("Goodbye!")
    except openai.APIConnectionError as e:
        print("Could not reach openAI server:", e.message)
        print(e.__cause__)
    except openai.RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
    except openai.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
        print(e.__cause__)
    except Exception as err:
        print("An error occured during the conversation with EPI:", err)
        print(err.__cause__)
    finally:
        print("This session had", llm_input_token_count, "input tokens and", llm_output_token_count, "output tokens")
        input_cost = llm_input_token_count * llm_input_token_cost[llm_model]
        output_cost = llm_output_token_count * llm_output_token_cost[llm_model]
        print("The cost for these is", input_cost, "kr and", output_cost, "kr respectively")
        print("Total cost was:", input_cost + output_cost, "kr")
        exit(0)

#first run DYLD_LIBRARY_PATH=/usr/local/lib /Users/epi/Code/ikaros/Bin/ikaros /Users/epi/epi-talking/Epi/ExperimentSetup.ikg -t -r25 EpiName=EpiWhite
# then wait until EPI says "Hello"
#then run with "python3 modeltest.py"


#Om ikaros kraschar så öka -r25 till -r250 ovan
#

#Problem: 

# Att skicka för långa ljudsekvenser med TTS till högtalaren resulterar i segfaults för att den inte kan kommunicera med huvudet
# Lösning: Använd macbookens högtalare...

# Dålig STT, kan inte många ord..
# Lösning: Byt till openAIs modell whisper som kan alla ord på alla språk.. (kostar $0.006 /minut )

# Dålig TTS
# Lösning: Byt till Whisper (kostar 15 USD/1M tecken)
