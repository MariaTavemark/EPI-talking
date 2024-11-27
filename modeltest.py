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

#Global
from random import random, shuffle
from configobj import ConfigObj
import time
import traceback

from tts import TTS
from epi import EPI

# Read our config from config.ini
config = ConfigObj("config.ini")

tts = TTS(config)
epi = EPI(config)

def checkKeypress():
    ch = input()
    if ch == 'v':
        print("Changing voices!")
        tts.next_voice()
    elif ch == 'n':
        print("Saying next line")
        return "Next"
    elif ch == 'i':
        epi.restartIkaros()
    elif ch == 'q':
        raise KeyboardInterrupt
    else:
        print("Invalid input: " + ch)
    return ""


def run_stt_to_llm():
    print("System ready")

    lang = config["Global"]["language"]

    for mood in epi.moods:
        print("EPI is " + mood)
        epi.setMood(mood)
        time.sleep(1)

    epi._nod_()
    epi._shakeHead_()
    epi.setMood("neutral")
    if lang == "sv":
        print("Saying hej!")
        tts.say("Hej!")
    else:
        print("Saying Hello!")
        tts.say("Hello!")

    while tts.isTalking():
        time.sleep(0.1)
    
    print("EPI is ready")
    print("To change to a random voice from the config, press 'v'")
    print("To make EPI say the next line, press 'n'")
    print("Press 'q' to quit")
    print("If EPI is not moving/changing colors, press 'i' to restart Ikaros")
    print("Please note that you need to press 'Enter' after each keypress for me to understand it")

    user_lines = config["Script"][lang]["user_lines"]
    epi_lines = config["Script"][lang]["epi_lines"]
    script_order = list(range(len(epi_lines)))
    index = 0

    #Remove the following two lines to always have the same order of lines in the script
    if (len(user_lines) == len(epi_lines)):
        shuffle(script_order)

    while (index < len(script_order)):
        res = checkKeypress()

        if not epi.ikarosRunning():
            print("Ikaros server has crashed... Trying to restart!")
            epi.startIkaros()
        
        if (res == "Next"):
            print("EPI is talking")

            happy_moods = ["glad", "happy"]
            angry_moods = ["arg", "angry"]
            sad_moods = ["ledsen", "sad"]
            neutral_moods = ["neutral", "neutral"]

            line = epi_lines[script_order[index]].split(' ')
            answer = ' '.join(line[:-1])
            if len(user_lines) > script_order[index]: 
                user_line = user_lines[script_order[index]]
            else:
                user_line = None
            index += 1
            
            mood = line[-1]
            print("EPI is saying: " + answer)

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

            tts.say(answer)

            #print("EPI is talking and flashing")
            while tts.isTalking():
                intensity = round(random()* 0.7, 1) + 0.1
                #print("Random mouth intensity: ", intensity)
                epi.controlEpi("mouth_intensity", intensity)
                time.sleep(0.1)

            epi.setMood("neutral")
            print("EPI is ready")
            if (user_line):
                print("We now expect the user to say " + user_line)


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
        epi.shutdown()
        print("Goodbye!")
        exit(0)


