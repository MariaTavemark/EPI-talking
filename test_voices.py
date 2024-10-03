#/Users/epi/miniforge3/bin/python3
import pyttsx3

tts_rate_desired = 130

engine = pyttsx3.init()

voices = engine.getProperty('voices')

#for voice in voices:
#    print(voice)
#    print()

#for voice in filter(lambda x: any([True for a in x.languages if "sv" in a]), voices):
#    print(voice)
#    print()

#exit(0)


print("Swedish voices")

sv_voices = list(filter(lambda x: "sv" in x.languages or "sv_SE" in x.languages, voices))
for voice in sv_voices:
    print(voice)
    print()

print("Trying Swedish voices, with no age")

for id, voice in enumerate(sv_voices):
    print("Voice is now ", voice.name, "and voice", voice)
    engine.setProperty('voice', voice.id) 
    engine.setProperty('rate', tts_rate_desired) 
    engine.say("Hej! Jag heter EPI och är en liten söt robot som testar sin röst för att se vilken som passar mig bäst!")
    engine.runAndWait()


print("English voices:")
en_codes = ["en", "en_GB", "en_US", "en_IN", "en_ZA", "en_IE", "en_AU", "en_GB_U_SD@sd=gbsct"]
en_voices = list(filter(lambda x: any([True for c in en_codes if c in x.languages]), voices))


print("Trying English voices, with no age")

for id, voice in enumerate(en_voices):
    print("Voice is now ", voice.name, "and voice", voice)
    engine.setProperty('voice', voice.id) 
    engine.setProperty('rate', tts_rate_desired) 
    engine.say("Hello! My name is EPI and I am a cute little robot who is testing its voice to see which one suits me the best")
    engine.runAndWait()