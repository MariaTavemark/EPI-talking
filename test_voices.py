#/Users/epi/miniforge3/bin/python3
import pyttsx3

tts_rate_desired = 130

engine = pyttsx3.init()

voices = engine.getProperty('voices')

for voice in voices:
    print(voice)
    print()


print("Swedish voices")

sv_voices = list(filter(lambda x: "sv" in x.languages or "sv_SE" in x.languages, voices))
for voice in sv_voices:
    print(voice)
    print()

print("Trying Swedish voices, with no age")

for id, voice in enumerate(sv_voices):
    print("Voice is now id", id, "and voice", voice)
    engine.setProperty('voice', voice.id) 
    engine.setProperty('rate', tts_rate_desired) 
    engine.say("Hej! Jag heter EPI och är en liten söt robot som testar sin röst för att se vilken som passar mig bäst!")
    engine.runAndWait()