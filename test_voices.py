#/Users/epi/miniforge3/bin/python3

voice_type = "avs"
tts_rate_desired_pyttsx3 = 130
tts_rate_desired_avspeech = 0.5
tts_rate_desired_avspeech_pitch = 0.55
en_codes = ["en", "en_GB", "en_US", "en_IN", "en_ZA", "en_IE", "en_AU", "en_GB_U_SD@sd=gbsct"]

def createTTS():
    tts_engine = AVSpeechSynthesizer()
    tts_engine.setUsesApplicationAudioSession_(False)
    return tts_engine

def createSv():
    sentence = "Hej! Jag heter EPI och är en liten söt robot som testar sin röst för att se vilken som passar mig bäst!"
    sentence_sv = AVSpeechUtterance()
    sentence_sv_pitch = AVSpeechUtterance()
    sentence_sv.setSpeechString_(sentence)
    sentence_sv_pitch.setSpeechString_(sentence)
    sentence_sv.setRate_(tts_rate_desired_avspeech)
    sentence_sv_pitch.setRate_(tts_rate_desired_avspeech_pitch)
    sentence_sv_pitch.setPitchMultiplier_(1.8)
    sentence_sv.setVolume_(1.0)
    sentence_sv_pitch.setVolume_(1.0)
    return (sentence_sv, sentence_sv_pitch)

def createEn():
    sentence = "Hello! My name is EPI and I am a cute little robot who is testing its voice to see which one suits me the best"
    sentence_en = AVSpeechUtterance()
    sentence_en_pitch = AVSpeechUtterance()
    sentence_en.setSpeechString_(sentence)
    sentence_en_pitch.setSpeechString_(sentence)
    sentence_en.setRate_(tts_rate_desired_avspeech)
    sentence_en_pitch.setRate_(tts_rate_desired_avspeech_pitch)
    sentence_en_pitch.setPitchMultiplier_(1.8)
    sentence_en.setVolume_(1.0)
    sentence_en_pitch.setVolume_(1.0)
    return (sentence_en, sentence_en_pitch)

if voice_type == "pyttsx3":
    import pyttsx3

    

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
        print("Voice is now ", '"' + voice.name + '"', "and voice", voice)
        engine.setProperty('voice', voice.id) 
        engine.setProperty('rate', tts_rate_desired_pyttsx3) 
        engine.say("Hej! Jag heter EPI och är en liten söt robot som testar sin röst för att se vilken som passar mig bäst!")
        engine.runAndWait()


    print("English voices:")
    en_voices = list(filter(lambda x: any([True for c in en_codes if c in x.languages]), voices))


    print("Trying English voices, with no age")

    for id, voice in enumerate(en_voices):
        print("Voice is now ", '"' + voice.name + '"', "and voice", voice)
        engine.setProperty('voice', voice.id) 
        engine.setProperty('rate', tts_rate_desired_pyttsx3) 
        engine.say("Hello! My name is EPI and I am a cute little robot who is testing its voice to see which one suits me the best")
        engine.runAndWait()

else:
    #Pitch is between 0.5 and 2.0
    from AppKit import AVSpeechSynthesizer, AVSpeechSynthesisVoice, AVSpeechUtterance
    import time
    #tts_engine.setOutputChannels_()
    voices = AVSpeechSynthesisVoice.speechVoices()

    sv_voices = list(filter(lambda x: "sv" in x.language() or "sv-SE" in x.language(), voices))
    en_voices = list(filter(lambda x: any([True for c in en_codes if c in x.language()]), voices))

    for v in sv_voices:
        print(v)
        print(v.identifier())
        tts_engine = createTTS()
        sentence_sv, sentence_sv_pitch = createSv()
        sentence_sv.setVoice_(v)
        sentence_sv_pitch.setVoice_(v)
        print(sentence_sv.volume())
        tts_engine.speakUtterance_(sentence_sv)
        while(tts_engine.isSpeaking()):
            time.sleep(0.2)
        tts_engine = createTTS()
        tts_engine.speakUtterance_(sentence_sv_pitch)
        while(tts_engine.isSpeaking()):
            time.sleep(0.2)

    for v in en_voices:
        print(v)
        print(v.identifier())
        tts_engine = createTTS()
        sentence_en, sentence_en_pitch = createEn()
        sentence_en.setVoice_(v)
        sentence_en_pitch.setVoice_(v)
        tts_engine.speakUtterance_(sentence_en)
        print(tts_engine.isSpeaking())
        while(tts_engine.isSpeaking()):
            time.sleep(0.2)
        tts_engine = createTTS()
        tts_engine.speakUtterance_(sentence_en_pitch)
        while(tts_engine.isSpeaking()):
            time.sleep(0.2)


    print(tts_engine.isSpeaking())
    print(tts_engine.outputChannels())
    print(tts_engine.audioDeviceId())