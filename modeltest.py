#/Users/epi/miniforge3/bin/python3

#####################################
#                                   #
#          BEGIN OF CONFIG          #
#                                   #
#####################################

#####################################
#                                   #
#        Project-wide config        #
#                                   #
#####################################
debug = False

# Set below to "sv" or "en" to change language of EPI
language = "sv"

#####################################
#                                   #
#           LLM config              #
#                                   #
#####################################
#LLM "local" or "online"
llm_type = "local"

#Which LLM should we use in online-mode?
llm_online_model = "gpt-4o-mini"
llm_online_default_keyfile = "/Volumes/MARIAT/openai.txt"

#Which LLM should we use in local-mode?
llm_local_model = "llama3.2:3b"

#On which port should the local LLM listen?
llm_local_port = 8888

#How do you run the local llm?
llm_local_command = "ollama serve"

#Where is ollama?
llm_local_bin = "/usr/local/bin/"

#Where is our home?
llm_local_home = "/Users/epi"

#What should the local llm environment variables be?
llm_local_env = {
    'OLLAMA_HOST': "127.0.0.1:" + str(llm_local_port),
    "PATH": llm_local_bin,
    "HOME": llm_local_home
                 }

#How random the answers should be [0.0-2.0]
llm_temperature = 0.8

#LLM base prompt in swedish
llm_sv_instructions = {"role": "system", "content": """
Du är EPI, en gullig robot som ska prata med sina vänner och känna igen dem. Du kan visa känslor, men ska 
generellt sett vara glad och snäll. Du får aldrig diskriminera någon. Användaren kan inte säga ditt namn på grund av dålig taligenkänning, så
om användaren verkar kalla dig något annat namn ska du ignorera det och fortsätta som vanligt. Använd inte några specialtecken i dina svar, utan bara a till ö och skiljetecken.
Avsluta ditt svar med att skriva en av följande fraser, baserat på hur EPI känner sig: arg, glad, ledsen, neutral
"""}

#LLM base prompt in english
llm_en_instructions = {"role": "system", "content": """
You are EPI, a cute robot who wants to talk to its friends and recognize them. You can show emotions, but you are generally happpy and nice.
The user cannot say your name due to bad speech recognition, so if they call you a different name - just ignore it and reply as usual.
Do not use any special characters in your answers, you may only use a-z and basic delimeters.
End your answer by writing a single word out of the following, based on how EPI is feeling: angry, happy, sad, neutral
"""}


#####################################
#                                   #
#           STT config              #
#                                   #
#####################################

#Which stt model should we use for swedish?
stt_sv_model = "vosk-model-small-sv-rhasspy-0.15"

#Which stt model should we use for english?
stt_en_model = "vosk-model-en-us-0.22"

#How large chunks (number of samples) should the STT use?
stt_chunk_size = 8000

#####################################
#                                   #
#            TTS config             #
#                                   #
#####################################

#What volume should we use (0.0-1.0)?
tts_volume_desired = 1.0

#How fast should we speak swedish?
tts_sv_rate_desired = 125

#How fast should we speak english?
tts_en_rate_desired = 125

#Which voice should we use for swedish?
tts_sv_voice = "Alva (Premium)"

#Which voice should we use for english?
tts_en_voice = "Sandy (English (US))"


#####################################
#                                   #
#             EPI config            #
#                                   #
#####################################

#Where can we reach Ikaros?
epi_url = "http://127.0.0.1:8000"

#What is the URL to control EPI?
epi_control_path = "/control/SR.positions/"



#####################################
#                                   #
#          END OF CONFIG            #
#   DO NOT CHANGE BELOW THIS BLOCK  #
#                                   #
#####################################

#Global
import sys
import select

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

# Local LLM:
import ollama
import subprocess


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

#Initialize global variables
epi_paused = False

#LLM key file setup
if llm_type == "online":
    try:
        if not os.path.isfile(llm_online_default_keyfile):
            print("Please select the key-file")
            Tk().withdraw()
            keyfile_path = askopenfilename()
        else:
            keyfile_path = llm_online_default_keyfile
        keyfile = open(keyfile_path, 'r')
        llm_org, llm_proj, llm_api_key = [k.removesuffix("\n") for k in keyfile.readlines()]
    except Exception as err:
        print("There was an error when opening the key-file. Shutting down.", err)
        exit(1)


#Initialize TTS variables
sv_lang_codes = ["sv", "sv_SE"]
en_lang_codes = ["en", "en_GB", "en_US", "en_IN", "en_ZA", "en_IE", "en_AU", "en_GB_U_SD@sd=gbsct"]

if language == "sv":
    tts_voice_name = tts_sv_voice
    tts_rate_desired = tts_sv_rate_desired
    lang_codes = sv_lang_codes
else:
    tts_voice_name = tts_en_voice
    tts_rate_desired = tts_en_rate_desired
    lang_codes = en_lang_codes

tts_engine = pyttsx3.init()
if debug:
    tts_rate = tts_engine.getProperty('rate') 
    print("Default speaking rate is:", tts_rate)
    tts_volume = tts_engine.getProperty('volume')
    print("Default tts volume is:", tts_volume)
    print("Our speaking rate is:", tts_rate_desired)
    print("Our tts volume is:", tts_volume_desired)
    print("Our tts voice choice is:", tts_voice_name)

tts_engine.setProperty('rate', tts_rate_desired) 
tts_engine.setProperty('volume',tts_volume_desired)

tts_voices = list(filter(lambda x: any([True for c in lang_codes if c in x.languages]), tts_engine.getProperty('voices')))
if len(tts_voices) == 0:
    tts_voices = tts_engine.getProperty('voices')

print("Available tts voices: ", len(tts_voices))

tts_voice = next((x.id for x in tts_voices if x.name == tts_voice_name), None)
if tts_voice is None:
    print("Could not find TTS voice", tts_voice_name)
    exit(1)

tts_engine.setProperty('voice', tts_voice if tts_voice else tts_voices[0].id) 
print("Pitch_base before: " + str(tts_engine.proxy._driver._tts._pitchBase()))
tts_engine.proxy._driver._tts._setPitchBase_(400)
print("Pitch_base after: " + str(tts_engine.proxy._driver._tts._pitchBase()))

#Initialize STT variables
stt_queue = queue.Queue()

stt_device = sounddevice.query_devices(kind='input')
stt_sample_rate = int(stt_device["default_samplerate"])

if language == "sv":
    stt_model_name= stt_sv_model
else:
    stt_model_name= stt_en_model

stt_model = vosk.Model(stt_model_name) 
stt = vosk.KaldiRecognizer(stt_model, stt_sample_rate)

# Method that is called whenever the audio stream gets data. Put audio in queue to be processed.
def stt_audio_add(indata, frames, time, status):
    if status:
        print("STT capture had status: ", status)
    if not epi_paused:
        stt_queue.put(bytes(indata))

stream = sounddevice.RawInputStream(samplerate=stt_sample_rate, blocksize = stt_chunk_size, device=stt_device['index'],
            dtype="int16", channels=1, callback=stt_audio_add)




# Initialize EPI-head variable
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
if language == "sv":
    llm_instructions = llm_sv_instructions
else:
    llm_instructions = llm_en_instructions

llm_message_history = [llm_instructions]


if llm_type == "online":
    llm_model=llm_online_model
    llm_client = OpenAI(
        organization=llm_org,
        project=llm_proj,
        api_key=llm_api_key
    )
elif llm_type == "local":
    llm_model = llm_local_model
    llm_server = subprocess.Popen(llm_local_command.split(" "), env=llm_local_env, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
    llm_started = False
    while not llm_started:
        print("Local LLM not yet started...")
        print(llm_server)
        if llm_server:
            row = llm_server.stderr.readline().decode("utf-8")
            llm_started = "Listening on" in row
            print("OLLAMA said: " + row)
        time.sleep(1)

    llm_client = ollama.Client(host="http://127.0.0.1:" + str(llm_local_port))


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

#Metod som ger svar baserat på en prompt/fråga
def generate_answer(prompt):
    global llm_input_token_count
    global llm_output_token_count

    message = {"role": "user", "content": prompt}
    llm_message_history.append(message)
    if llm_type == "online":
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
    else:
        response = llm_client.chat(model=llm_model, 
                               options={
                                  "temperature": llm_temperature
                               },
                               messages=llm_message_history)
        return response['message']['content']


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
        return None
    

def control_epi(channel, value):
    if channel not in epi_channels:
        raise ValueError("Invalid EPI channel sent:", channel)
    valid_values = epi_valid_ranges[channel]
    if valid_values[0] <= value <= valid_values[1]:
         requests.get(epi_url + epi_control_path + str(epi_channels[channel]) + "/0/" + str(value), timeout=0.1)



#Create epi moods below


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
    delay = 0.03 #About 30 Hz

    step = 4
    shake_moves = []
    shake_moves.extend(range(0, -degrees, -step))
    shake_moves.extend(range(-degrees, degrees, step))
    shake_moves.extend(range(degrees, 0 + step, -step))

    for i in range(num_shakes):
        for j in shake_moves:
            control_epi("neck_pan", j)
            time.sleep(delay)

    control_epi("neck_pan", 0)

def epi_nod():
    num_shakes = 2
    min_degrees = 0
    max_degrees = 15
    delay = 0.03 # About 30 Hz

    step = 4
    nod_moves = []
    nod_moves.extend(range(0, min_degrees, -step))
    nod_moves.extend(range(min_degrees, max_degrees, step))
    nod_moves.extend(range(max_degrees, 0 + step, -step))

    for i in range(num_shakes):
        for j in nod_moves:
            control_epi("neck_tilt", j)
            time.sleep(delay)
    control_epi("neck_tilt", 0)


def epi_thinking():
    control_epi("left_pupil", 50)
    control_epi("right_pupil", 50)
    time.sleep(0.5)


def epi_done_thinking():
    control_epi("left_pupil", 20)
    control_epi("right_pupil", 20)


def newTTSthread():
    return threading.Thread(target=tts_engine.runAndWait())


# Method to check if we should pause EPI
def checkKeypress():
    global epi_paused
    global llm_message_history
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        ch = sys.stdin.read(1)
        if ch == 'p':
            epi_paused = not epi_paused
            print("EPI is now " + ("" if not epi_paused else "not ") + "listening. Press 'p' to make EPI " + ("" if epi_paused else "not ") + "listen")
        elif ch == 'r':
            llm_message_history = [llm_instructions]
            print("Chat history cleared, the conversation with EPI has now started over.")


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
    
    print("Saying hej!")
    tts_engine.say("Hej!")
    tts_thread:threading.Thread = newTTSthread()
    tts_thread.start()

    while tts_thread.is_alive():
        time.sleep(0.1)
    
    stream.start()
    print("EPI is listening")
    print("To make EPI pause (and not listen), press 'p'")
    print("Press 'r' to reset the conversation with EPI")

    while True:
        checkKeypress()
        if epi_paused:
            time.sleep(0.2)
            continue

        result = stt_recognize()
        #Test if we recognized any speech
        if result:
            if debug: print("Recognized text was:", result)
            print("You said:", result)
            #Pass to LLM
            epi_thinking()
            print("EPI is thinking....")
            answer = generate_answer(result).split()
            if debug: print("Answer was:", answer)
            epi_done_thinking()

            #Pass to TTS
            stream.stop()


            print("EPI is talking")
            print("EPI said: ", " ".join(answer[:-1]))
            mood:str = answer[-1:][0]

            happy_moods = ["glad", "happy"]
            angry_moods = ["arg", "angry"]
            sad_moods = ["ledsen", "sad"]
            neutral_moods = ["neutral", "neutral"]

            if any([True for x in happy_moods if x in mood.lower()]):
                print("EPI is happy")
                epi_happy()
            elif any([True for x in angry_moods if x in mood.lower()]):
                print("EPI is angry")
                epi_angry()
            elif any([True for x in sad_moods if x in mood.lower()]):
                print("EPI is sad")
                epi_sad()
            else:
                print("Epi had the mood", mood.lower())
                epi_neutral()
            
            no_codes = ["nej,", "nej", "nej.", "nej!", "nej?", "no,", "no", "no.", "no!", "no?"]
            yes_codes = ["ja,", "ja", "ja.", "ja!", "ja?", "yes,", "yes", "yes.", "yes!", "yes?"]
            if any([True for x in answer[:-1] if x.lower() in no_codes]):
                threading.Thread(target=epi_shake_head()).start()
            elif any([True for x in answer[:-1] if x.lower() in yes_codes]):
                threading.Thread(target=epi_nod()).start()

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
        if llm_type == "online":
            print("This session had", llm_input_token_count, "input tokens and", llm_output_token_count, "output tokens")
            input_cost = llm_input_token_count * llm_input_token_cost[llm_model]
            output_cost = llm_output_token_count * llm_output_token_cost[llm_model]
            print("The cost for these is", input_cost, "kr and", output_cost, "kr respectively")
            print("Total cost was:", input_cost + output_cost, "kr")
        else:
            llm_server.kill()
            print("Goodbye!")
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
