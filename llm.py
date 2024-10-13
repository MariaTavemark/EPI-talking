from random import random
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os.path
from openai import OpenAI
import traceback
import openai

import ollama
import subprocess
#{"role": "system", "content":

#    
class LLM:
    in_token_cost = {
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

    out_token_cost = {
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



    def __init__(self, config):
        self.in_tokens = 0
        self.out_tokens = 0

        llm_conf = config['LLM']
        self.llm_type = llm_conf['type']
        self.temperature = float(llm_conf['temperature'])
        t_conf = llm_conf[self.llm_type]
        self.lang = config["Global"]["language"]

        self.message_history = list()
        prompt = llm_conf[self.lang]["instructions"]
        self.instructions = {"role": "system", "content": prompt}
        self.message_history.append(self.instructions)

        self.model = llm_conf[self.llm_type]["model"]

        if self.llm_type == "online":
            try:
                def_keyfile = t_conf["default_keyfile"]
                if not os.path.isfile(def_keyfile):
                    print("Please select the key-file")
                    Tk().withdraw()
                    keyfile_path = askopenfilename()
                else:
                    keyfile_path = def_keyfile
                keyfile = open(keyfile_path, 'r')
                tmp = [k.removesuffix("\n") for k in keyfile.readlines()]
                llm_org, llm_proj, llm_api_key = tmp
            except Exception as err:
                print("There was an error when opening the key-file. Shutting down.", err)
                exit(1)

            self.client = OpenAI(
                organization=llm_org,
                project=llm_proj,
                api_key=llm_api_key
            )
        
        elif self.llm_type == "local":
            command =  t_conf["command"]
            port = str(t_conf["port"])
            env = {
                'OLLAMA_HOST': "127.0.0.1:" + port,
                'PATH': t_conf["bin"],
                'HOME': t_conf["home"]
            }
            self.server = subprocess.Popen(
                command.split(" "),
                env=env, 
                stderr=subprocess.PIPE,
                stdout=subprocess.DEVNULL
                )
            
            llm_started = False
            while not llm_started:
                print("Local LLM not yet started...")
                if self.server:
                    row = self.server.stderr.readline().decode("utf-8")
                    llm_started = "Listening on" in row
                    print("OLLAMA said: " + row)
                time.sleep(1)

            self.client = ollama.Client(host="http://127.0.0.1:" + port)


    def _generateAnswer_(self, prompt):
        message = {"role": "user", "content": prompt}
        self.message_history.append(message)

        if self.llm_type == "online":
            out = self.client.chat.completions.create(
                model=self.model,
                messages=self.message_history,
                temperature=self.temperature,
                n=1,
                max_completion_tokens=1000,
                timeout=10
            )

            reply = out.choices[0].message.content
            role = out.choices[0].message.role
            self.message_history.append({"role": role, "content": reply})

            self.in_tokens += out.usage.prompt_tokens
            self.out_tokens += out.usage.completion_tokens
        
            return reply
        
        elif self.llm_type == "local":
            response = self.client.chat(model=self.model, 
                               options={
                                  "temperature": self.temperature
                               },
                               messages=self.message_history)["message"]
        
            self.message_history.append({"role": response["role"], 
                                         "content": response["content"]})
            return response['content']
        

    def generateAnswer(self, prompt):
        try:
            return self._generateAnswer_(prompt)
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
        except Exception as e:
            print("Something went wrong when generating an answer")
            print(traceback.format_exc())
        
        return ""
    

    def getCost(self):
        input_cost = self.in_tokens * self.in_token_cost[self.model]
        output_cost = self.out_tokens * self.out_token_cost[self.model]
        return {
            "input": input_cost,
            "output": output_cost,
            "total": input_cost + output_cost
            }
    

    def shutdown(self):
        if self.llm_type == "online":
            cost = self.getCost()
            print("This session had", self.in_tokens, "input tokens and", self.in_tokens, "output tokens")
            print("The cost for these is", cost["input"], "kr and", cost["output"], "kr respectively")
            print("Total cost was:", cost["total"], "kr")
        else:
            self.server.kill()
            time.sleep(1)
            self.server.terminate()
        
    
    def clearHistory(self):
        self.message_history = [self.instructions]
