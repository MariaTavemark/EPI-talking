#/Users/epi/miniforge3/bin/python3

#LLM key file choosing
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# LLM:
from openai import OpenAI
import json

#STT:
import openai
import vosk
import queue
import json
import sounddevice

#TTS:
import pyttsx3

debug = False


#LLM key file config
try:
    print("Please select the key-file")
    Tk().withdraw()
    keyfile_path = askopenfilename()
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

tts_voice = 0 # Ok voices seem to be 88(male), 69(female), 2, 3, 13
#Funny values on the above (robotic/strange): 40, 61, 87, 113, 118, 139, 140, 144

tts_engine = pyttsx3.init(driverName="espeak")

tts_rate = tts_engine.getProperty('rate') 
print("Default speaking rate is:", tts_rate)
tts_engine.setProperty('rate', tts_rate_desired) 
print("Our speaking rate is:", tts_rate_desired)

tts_volume = tts_engine.getProperty('volume')
print("Default tts volume is:", tts_volume)
tts_engine.setProperty('volume',tts_volume_desired)
print("Our tts volume is:", tts_volume_desired)

tts_voices = list(filter(lambda x: 'sv' in x.languages, tts_engine.getProperty('voices')))
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
#prompt = "Hej, jag heter Maria. Vad heter du?"
#print("Generating answer for prompt: ", prompt)
#print(generate_answer(prompt))  

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
    print("System ready")
    while True:
        result = stt_recognize()
        #Test if we recognized any speech
        if result:
            if debug: print("Recognized text was:", result)
            print("You said:", result)
            #Pass to LLM
            print("EPI is thinking....")
            answer = generate_answer(result)
            if debug: print("Answer was:", answer)
            #Pass to TTS
            stream.stop()
            print("EPI is talking")
            print("EPI said: ", answer)
            tts_engine.say(answer)
            tts_engine.runAndWait()
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
        print(err.__traceback__)
    finally:
        print("This session had", llm_input_token_count, "input tokens and", llm_output_token_count, "output tokens")
        input_cost = llm_input_token_count * llm_input_token_cost[llm_model]
        output_cost = llm_output_token_count * llm_output_token_cost[llm_model]
        print("The cost for these is", input_cost, "kr and", output_cost, "kr respectively")
        print("Total cost was:", input_cost + output_cost, "kr")
        exit(0)


#run with "python3 modeltest.py"


#Summering: 
# Allt fungerar jättebra, såvida vi får en maskin med en RTX 4+70/4080 att köra på. Att köra en LLM lokalt kräver en del resurser....
# STT kommer inte kunna identifiera "EPI" som ord, såvida vi inte tränar den. Vilket kräver en bättre maskin än vår laptop.