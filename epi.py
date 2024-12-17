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


import subprocess
import threading
import time

import requests


class EPI:
    channels = {
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

    valid_ranges = {
        "neck_tilt": (-55, 55),
        "neck_pan": (-30, 30),
        "left_eye": (-20, 20),
        "right_eye": (-20, 20),
        "left_pupil": (5, 90),
        "right_pupil": (5, 90),
        "eyes_r": (0, 100),
        "eyes_g": (0, 100),
        "eyes_b": (0, 100),
        "eyes_intensity": (0.0, 1.0),
        "mouth_r": (0, 100),
        "mouth_g": (0, 100),
        "mouth_b": (0, 100),
        "mouth_intensity": (0.0, 1.0),
        "sound_clip": (0, 10)
    }


    moods = {
        "neutral": {
            "mouth_intensity": 0.2,
            "mouth_r": 50,
            "mouth_g": 50,
            "mouth_b": 50,
            "eyes_r": 50,
            "eyes_g": 50,
            "eyes_b": 50,
            "eyes_intensity": 0.2,
            "left_pupil": 20,
            "right_pupil": 20,
        },
        "sad": {
            "mouth_intensity": 0.2,
            "mouth_r": 0,
            "mouth_g": 0,
            "mouth_b": 100,
            "eyes_r": 0,
            "eyes_g": 0,
            "eyes_b": 100,
            "eyes_intensity": 0.2,
            "left_pupil": 90,
            "right_pupil": 90,
        },
        "happy": {
            "mouth_intensity": 0.6,
            "mouth_r": 0,
            "mouth_g": 100,
            "mouth_b": 0,
            "eyes_r": 0,
            "eyes_g": 50,
            "eyes_b": 0,
            "eyes_intensity": 0.8,
            "left_pupil": 50,
            "right_pupil": 50,
        },
        "angry": {
            "mouth_intensity": 1.0,
            "mouth_r": 100,
            "mouth_g": 0,
            "mouth_b": 0,
            "eyes_r": 100,
            "eyes_g": 0,
            "eyes_b": 0,
            "eyes_intensity": 1.0,
            "left_pupil": 5,
            "right_pupil": 5,
        },
        "thinking": {
            "left_pupil": 5,
            "right_pupil": 5,
        },
        "done_thinking": {
            "left_pupil": 50,
            "right_pupil": 50,
        }
    }


    def __init__(self, config):
        epi_conf = config["EPI"]
        ikaros_conf = epi_conf["ikaros"]
        bin = ikaros_conf["binary"]
        file = ikaros_conf["file"]
        epi_type = epi_conf["type"]

        self.epi_url = epi_conf["url"]
        self.control_path = epi_conf["control_path"]

        self.command = bin + " " + file + " -t -r EpiName=" + epi_type
        ikaros_env = ikaros_conf["env"]
        self.env = {ikaros_env[0]: ikaros_env[1]}

        self.startIkaros()


    def ikarosProcess(self):
        return subprocess.Popen(self.command.split(" "), 
                                env=self.env, 
                                stderr=subprocess.STDOUT, 
                                stdout=subprocess.PIPE
                                )
    

    def startIkaros(self):
        self.server = self.ikarosProcess()
        ikaros_started = False
        while not ikaros_started:
            print("EPI - Ikaros has not yet started...")
            if self.server and self.server.poll() is not None:
                print("EPI - Ikaros has crashed...")
                for row in self.server.stdout.readlines():
                    print("EPI - Ikaros said: " + row.decode("utf-8"))
                self.server = self.ikarosProcess()

            elif self.server:
                row =  self.server.stdout.readline().decode("utf-8")
                print("EPI - Ikaros said: " + row)
                started_string = "IKAROS: 1 WARNING."
                starting_string = "Power off servos."
                if started_string in row:
                    print("EPI - Ikaros has started, waiting for motors to power on..")
                    time.sleep(5)
                    ikaros_started = True
                if starting_string in row:
                    print("EPI - Ikaros will be started in 15 seconds")
                    time.sleep(15)
                    if self.server.poll() is None:
                        ikaros_started = True
                        print("EPI - Ikaros has started!")
            time.sleep(0.2)


    def ikarosRunning(self):
        return self.server.poll() is None
    

    def shutdown(self):
        self.server.terminate()
        time.sleep(5)
        self.server.kill()


    def terminateIkaros(self):
        if self.server:
            self.server.terminate()


    def restartIkaros(self):
        print("EPI - Restarting ikaros. Please wait!")
        self.terminateIkaros()
        self.startIkaros()



    def controlEpi(self, channel, value, tries=0):
        if channel not in self.channels:
            raise ValueError("EPI - Invalid EPI channel sent:", channel)
        valid_values = self.valid_ranges[channel]
        if valid_values[0] <= value <= valid_values[1]:
            try:
                req = self.epi_url + self.control_path + str(self.channels[channel]) + "/0/" + str(value)
                requests.get(req, timeout=0.25)
            except Exception as err:
                print("EPI - An error occurred when communicating with EPI. Assuming that Ikaros is unresponsive..")
                if tries < 5:
                    print("EPI - Restarting ikaros... Please wait...")
                    self.restartIkaros()
                    self.controlEpi(channel, value, tries + 1)
                else:
                    raise err
                

    def setMood(self, mood):
        if mood not in self.moods:
            raise ValueError("EPI - Invalid EPI mood sent:", mood)
        actions = self.moods[mood]

        for channel, value in actions.items():
            self.controlEpi(channel, value)


    def _nod_(self):
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
                self.controlEpi("neck_tilt", j)
                time.sleep(delay)

        self.controlEpi("neck_tilt", 0)


    def _shakeHead_(self):
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
                self.controlEpi("neck_pan", j)
                time.sleep(delay)

        self.controlEpi("neck_pan", 0)

    
    def nod(self):
        threading.Thread(target=self._nod_).start()


    def shakeHead(self):
        threading.Thread(target=self._shakeHead_).start()