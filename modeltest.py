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
import tty
import sys

from tts import TTS
from epi import EPI

class ModelTest:
    def ModelTest(self):
        tty.setcbreak(sys.stdin)

        # Read our config from config.ini
        self.config = ConfigObj("config.ini")

        self.tts = TTS(self.config)
        self.epi = EPI(self.config)

        self.index = 0



    def checkKeypress(self):
        #ch = input()
        ch = sys.stdin.read(1)
        if ch == 'v':
            print("Changing voices!")
            self.tts.next_voice()
        elif ch == 'n':
            print("Saying line", self.index + 1, "out of", self.num_lines)
            return "Next"
        elif ch == 'i':
            self.epi.restartIkaros()
        elif ch == 'q':
            raise KeyboardInterrupt
        else:
            print("Invalid input: " + ch)
        return ""


    def run_stt_to_llm(self):
        print("System ready")

        lang = self.config["Global"]["language"]

        for mood in self.epi.moods:
            print("EPI is " + mood)
            self.epi.setMood(mood)
            time.sleep(1)

        self.epi._nod_()
        self.epi._shakeHead_()
        self.epi.setMood("neutral")
        if lang == "sv":
            print("Saying hej!")
            self.tts.say("Hej!")
        else:
            print("Saying Hello!")
            self.tts.say("Hello!")

        while self.tts.isTalking():
            time.sleep(0.1)
        
        print("EPI is ready")
        print("To change to a random voice from the config, press 'v'")
        print("To make EPI say the next line, press 'n'")
        print("Press 'q' to quit")
        print("If EPI is not moving/changing colors, press 'i' to restart Ikaros")
        
        #No longer needed...
        #print("Please note that you need to press 'Enter' after each keypress for me to understand it")

        user_lines = self.config["Script"][lang]["user_lines"]
        epi_lines = self.config["Script"][lang]["epi_lines"]
        script_order = list(range(len(epi_lines)))
        self.num_lines = len(epi_lines)

        #Remove the following two lines to always have the same order of lines in the script
        if (len(user_lines) == len(epi_lines)):
            shuffle(script_order)

        while (True):
            if self.index >= len(script_order):
                self.index = 0
                self.tts.next_voice()
                print("I have gone through all lines and have now changed to the next voice!")
            res = self.checkKeypress()

            if not self.epi.ikarosRunning():
                print("Ikaros server has crashed... Trying to restart!")
                self.epi.startIkaros()
            
            if (res == "Next"):
                #print("EPI is talking")

                happy_moods = ["glad", "happy"]
                angry_moods = ["arg", "angry"]
                sad_moods = ["ledsen", "sad"]
                neutral_moods = ["neutral", "neutral"]

                line = epi_lines[script_order[self.index]].split(' ')
                answer = ' '.join(line[:-1])
                if len(user_lines) > script_order[self.index]: 
                    user_line = user_lines[script_order[self.index]]
                else:
                    user_line = None
                self.index += 1
                
                mood = line[-1]
                print("EPI is saying: " + answer)

                if any([True for x in happy_moods if x in mood.lower()]):
                    #print("EPI is happy")
                    self.epi.setMood("happy")
                elif any([True for x in angry_moods if x in mood.lower()]):
                    #print("EPI is angry")
                    self.epi.setMood("angry")
                elif any([True for x in sad_moods if x in mood.lower()]):
                    #print("EPI is sad")
                    self.epi.setMood("sad")
                else:
                    #print("Epi had the mood", mood.lower())
                    self.epi.setMood("neutral")
                

                no_codes = ["nej,", "nej", "nej.", "nej!", "nej?", "no,", "no", "no.", "no!", "no?"]
                yes_codes = ["ja,", "ja", "ja.", "ja!", "ja?", "yes,", "yes", "yes.", "yes!", "yes?"]
                if any([True for x in answer if x.lower() in no_codes]):
                    self.epi.shakeHead()
                elif any([True for x in answer if x.lower() in yes_codes]):
                    self.epi.nod()

                self.tts.say(answer)

                #print("EPI is talking and flashing")
                while self.tts.isTalking():
                    intensity = round(random()* 0.7, 1) + 0.1
                    #print("Random mouth intensity: ", intensity)
                    self.epi.controlEpi("mouth_intensity", intensity)
                    time.sleep(0.1)

                self.epi.setMood("neutral")
                #print("EPI is ready")
                if (user_line):
                    print("We now expect the user to say " + user_line)





if __name__ == "__main__":
    try:
        model = ModelTest()
        for _ in range(100):
            print()
        model.run_stt_to_llm()
    except KeyboardInterrupt as k:
        print("Goodbye!")
    except Exception as err:
        print("An error occured during the conversation with EPI:", err)
        print(traceback.format_exc())
    finally:
        model.epi.shutdown()
        print("Goodbye!")
        exit(0)