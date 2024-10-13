#/Users/epi/miniforge3/bin/python3

#Global
from random import random
import sys
import select
from configobj import ConfigObj
import time
import traceback

from tts import TTS
from llm import LLM
from stt import STT
from epi import EPI

# Read our config from config.ini
config = ConfigObj("config.ini")

tts = TTS(config)
llm = LLM(config)
stt = STT(config)
epi = EPI(config)

def checkKeypress():
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        ch = sys.stdin.read(1)
        if ch == 'p':
            stt.pause()
            print("EPI is now " + ("" if not stt.paused else "not ") + "listening. Press 'p' to make EPI " + ("" if stt.paused else "not ") + "listen")
        elif ch == 'r':
            llm.clearHistory()
            print("Chat history cleared, the conversation with EPI has now started over.")
        elif ch == 'i':
            epi.restartIkaros()
        elif ch == 'q':
            raise KeyboardInterrupt


def run_stt_to_llm():
    print("System ready")

    for mood in epi.moods:
        print("EPI is " + mood)
        epi.setMood(mood)
        time.sleep(1)

    epi._nod_()
    epi._shakeHead_()
    epi.setMood("neutral")
    
    print("Saying hej!")
    tts.say("Hej!")
    while tts.isTalking():
        time.sleep(0.1)
    
    stt.resume()

    print("EPI is listening")
    print("To make EPI pause (and not listen), press 'p'")
    print("Press 'r' to reset the conversation with EPI")
    print("Press 'q' to quit")
    print("If EPI is not moving/changing colors, press 'i' to restart Ikaros")
    print("Please note that you need to press 'Enter' after each keypress for me to understand it")

    while True:
        checkKeypress()

        if not epi.ikarosRunning():
            print("Ikaros server has crashed... Trying to restart!")
            stt.pause()
            epi.startIkaros()
            stt.resume()

        if stt.paused:
            time.sleep(0.2)
            continue

        result = stt.recognize()
        #Test if we recognized any speech
        if result:
            print("You said:", result)

            #Pass to LLM
            epi.setMood("thinking")
            print("EPI is thinking....")

            answer = llm.generateAnswer(result).split()
            epi.setMood("done_thinking")

            #Pass to TTS
            stt.pause()

            print("EPI is talking")
            if llm.llm_type == "local":
                print("EPI said: ", " ".join(answer))
                mood = "neutral"
            else:
                print("EPI said: ", " ".join(answer[:-1]))
                mood = answer[-1:][0]
                answer = answer[:-1]

            happy_moods = ["glad", "happy"]
            angry_moods = ["arg", "angry"]
            sad_moods = ["ledsen", "sad"]
            neutral_moods = ["neutral", "neutral"]

            if any([True for x in happy_moods if x in mood.lower()]):
                print("EPI is happy")
                epi.setMood("happy")
            elif any([True for x in angry_moods if x in mood.lower()]):
                print("EPI is angry")
                epi.setMood("angry")
            elif any([True for x in sad_moods if x in mood.lower()]):
                print("EPI is sad")
                epi.setMood("sad")
            else:
                print("Epi had the mood", mood.lower())
                epi.setMood("neutral")
            

            no_codes = ["nej,", "nej", "nej.", "nej!", "nej?", "no,", "no", "no.", "no!", "no?"]
            yes_codes = ["ja,", "ja", "ja.", "ja!", "ja?", "yes,", "yes", "yes.", "yes!", "yes?"]
            if any([True for x in answer if x.lower() in no_codes]):
                epi.shakeHead()
            elif any([True for x in answer if x.lower() in yes_codes]):
                epi.nod()

            tts.say(" ".join(answer))

            #print("EPI is talking and flashing")
            while tts.isTalking():
                intensity = int(random() * 30)
                #print("Random mouth intensity: ", intensity)
                epi.controlEpi("mouth_intensity", intensity)
                time.sleep(0.2)

            epi.setMood("neutral")
            stt.resume()
            print("EPI is listening")


if __name__ == "__main__":
    try:
        for _ in range(100):
            print()
        run_stt_to_llm()
    except KeyboardInterrupt as k:
        print("Goodbye!")
    except Exception as err:
        print("An error occured during the conversation with EPI:", err)
        print(traceback.format_exc())
    finally:
        llm.shutdown()
        epi.shutdown()
        print("Goodbye!")
        exit(0)


#Problem: 

# Dålig STT, kan inte många ord..
# Lösning: Byt till openAIs modell whisper som kan alla ord på alla språk.. (kostar $0.006 /minut )

# Dålig TTS
# Lösning: Byt till Whisper (kostar 15 USD/1M tecken)

#TODO:
#Testa vuxen engelska
#Testa vuxen svenska
#Testa barn engelska
#Testa pyttsx3 svenska
#Testa pyttsx3 engelska
#Testa online LLM svenska
#Testa online LLM engelska
