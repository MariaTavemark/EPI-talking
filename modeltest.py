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
    no_codes = ["nej,", "nej", "nej.", "nej!", "nej?", "no,", "no", "no.", "no!", "no?"]
    yes_codes = ["ja,", "ja", "ja.", "ja!", "ja?", "yes,", "yes", "yes.", "yes!", "yes?"]

    happy_moods = ["glad", "happy"]
    angry_moods = ["arg", "angry"]
    sad_moods = ["ledsen", "sad"]
    neutral_moods = ["neutral", "neutral"]

    def __init__(self):
        tty.setcbreak(sys.stdin)

        # Read our config from config.ini
        self.config = ConfigObj("config.ini")

        # Initialize epi and the tts
        self.tts = TTS(self.config)
        self.epi = EPI(self.config)

        # Keep track of which line we are at
        self.index = 0

        self.lang = self.config["Global"]["language"]
        self.user_lines = self.config["Script"][self.lang]["user_lines"]
        self.epi_lines = self.config["Script"][self.lang]["epi_lines"]
        self.num_lines = len(self.epi_lines)
        self.script_order = list(range(self.num_lines))

        #Remove the following two lines to always have the same order of lines in the script
        if (len(self.user_lines) == len(self.epi_lines)):
            shuffle(self.script_order)
        

    def checkKeypress(self):
        ch = sys.stdin.read(1)
        if ch == 'v':
            self.nextVoice()
            self.index = 0
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
    

    def nextVoice(self):
        if self.tts.next_voice() == "Done":
            print()
            print("We are now done. Please press 'n' when you are ready to run the summary of all voices. (press 's' to step through the summary)")
            print()
            ch = sys.stdin.read(1)
            while (ch != 'n' and ch != 's'):
                time.sleep(0.1)
                ch = sys.stdin.read(1)

            if ch == 'n':
                self.run_summary()
            else: 
                self.step_summary()
            return "Done"
        print("Changing voices to", self.tts.name, self.tts.get_progress())


    def run_summary(self):
        print("I am now running the summary")
        line,_,_ = self.getLine(0)
        self.tts.summary(line)


    def step_summary(self):
        print()
        print("I am now stepping through the summary. Press 'n' to hear the next voice.")
        line,_,_ = self.getLine(0)
        for i in self.tts.used_voices:
            self.tts.summary_step(line, i)
            print()
            ch = sys.stdin.read(1)
            while ch != 'n':
                time.sleep(0.1)
                ch = sys.stdin.read(1)


    def getLine(self, index = -1):
        # Get next line and split into mood and rest, also handle user lines
        i = self.script_order[self.index] if index == -1 else index
        line = self.epi_lines[i].split(' ')
        answer = ' '.join(line[:-1])
        mood = line[-1]
        if len(self.user_lines) > i: 
            user_line = self.user_lines[i]
        else:
            user_line = None

        if index == -1:
            self.index += 1 

        return answer, mood, user_line


    def run_stt_to_llm(self):
        for mood in self.epi.moods:
            #print("EPI is " + mood)
            self.epi.setMood(mood)
            time.sleep(1)

        self.epi._nod_()
        self.epi._shakeHead_()
        self.epi.setMood("neutral")
        if self.lang == "sv":
            #print("Saying hej!")
            self.tts.say("Hej!")
        else:
            #print("Saying Hello!")
            self.tts.say("Hello!")

        while self.tts.isTalking():
            time.sleep(0.1)
        
        print("System ready, using", self.tts.name)
        #print("EPI is ready")
        print("To change to a random voice from the config, press 'v'")
        print("To make EPI say the next line, press 'n'")
        print("Press 'q' to quit")
        print("If EPI is not moving/changing colors, press 'i' to restart Ikaros")
        print()

        while (True):
            if self.index >= len(self.script_order):
                self.index = 0
                if self.nextVoice() == "Done":
                    return
                print("I have gone through all lines and changed voices automatically.")
                print()
            res = self.checkKeypress()

            if not self.epi.ikarosRunning():
                print("Ikaros server has crashed... Trying to restart!")
                self.epi.startIkaros()
            
            if (res == "Next"):
                answer, mood, user_line = self.getLine()
                
                print("EPI is saying: " + answer)

                if any([True for x in self.happy_moods if x in mood.lower()]):
                    self.epi.setMood("happy")
                elif any([True for x in self.angry_moods if x in mood.lower()]):
                    self.epi.setMood("angry")
                elif any([True for x in self.sad_moods if x in mood.lower()]):
                    self.epi.setMood("sad")
                else:
                    self.epi.setMood("neutral")
                
                if any([True for x in answer if x.lower() in self.no_codes]):
                    self.epi.shakeHead()
                elif any([True for x in answer if x.lower() in self.yes_codes]):
                    self.epi.nod()

                self.tts.say(answer)

                while self.tts.isTalking():
                    intensity = round(random()* 0.7, 1) + 0.1
                    self.epi.controlEpi("mouth_intensity", intensity)
                    time.sleep(0.1)

                self.epi.setMood("neutral")
                if (user_line):
                    print("We now expect the user to say " + user_line)
                print()



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