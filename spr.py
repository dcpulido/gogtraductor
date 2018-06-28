#!/usr/bin/env python3
# Requires PyAudio and PySpeech.
import os
import  sys
from googletrans import Translator
import speech_recognition as sr
from google.cloud import texttospeech_v1beta1
from playsound import playsound
import configparser
import logging


def ConfigSectionMap(section,
                     Config):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                logging.info('skip: %s' % option)
        except:
            logging.info('exception on %s!' % option)
            dict1[option] = None
    return dict1


def get_general_conf(name):
    Config = configparser.ConfigParser()
    Config.read('./conf/config.conf')
    myprior = {}
    for sec in Config.sections():
        if sec == name:
            myprior = ConfigSectionMap(sec, Config)
    return myprior


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("SAY SOMETHING!")
        return r.listen(source)


def recognise_audio(audio, lang):
    try:
        r = sr.Recognizer()
        return r.recognize_google(audio,
                                  language=lang)
    except sr.UnknownValueError:
        print("could not understand audio")
    except sr.RequestError as e:
        print("Could not request {0}".format(e))


def translate(text,
              language):
    translator = Translator()
    lang = language.split("-")[0]
    return translator.translate(text, dest=lang)


def tx_to_sp(tx,
             language):
    client = texttospeech_v1beta1.TextToSpeechClient()
    input_text = texttospeech_v1beta1.types.SynthesisInput(text=tx.text)

    voice = texttospeech_v1beta1.types.VoiceSelectionParams(
        language_code=language,
        ssml_gender=texttospeech_v1beta1.enums.SsmlVoiceGender.FEMALE)

    audio_config = texttospeech_v1beta1.types.AudioConfig(
        audio_encoding=texttospeech_v1beta1.enums.AudioEncoding.MP3)

    return client.synthesize_speech(input_text,
                                    voice,
                                    audio_config)


def play_sound(data):
    with open('output.mp3', 'wb') as out:
        out.write(data.audio_content)
        playsound('./output.mp3')
        os.system("rm ./output.mp3")

def usage():
    toret = "python3 " + sys.argv[0] + "\n"
    toret += "\tno arguments default behaviour\n"
    toret += "\t-h help\n"
    toret += "\t-i language input (en-US fr-FR es-ES ...) \n"
    toret += "\t-o language output (en-US fr-FR es-ES ...) \n"
    return toret

if __name__ == '__main__':
    language_conf = get_general_conf("lang")
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == "-h":
                print(usage())
                sys.exit(0)
            if sys.argv[i] == "-i":
                try:
                    language_conf["lang_input"] = sys.argv[i+1]
                except Exception:
                    print("FAI AS COUSAS BEN CARALLO!!")
                    print(usage())
                    sys.exit(0)
            if sys.argv[i] == "-0":
                try:
                    language_conf["lang_output"] = sys.argv[i+1]
                except Exception:
                    print("FAI AS COUSAS BEN CARALLO!!")
                    print(usage())
                    sys.exit(0)
    print("AKKA TRADUCtOR")
    print("INPUT: " + language_conf["lang_input"])
    print("OUTPUT: " + language_conf["lang_output"])
    try:
        while True:
            input("NEXT!! (enter)")
            audio = get_audio()
            recognition = recognise_audio(audio, language_conf["lang_input"])
            print("RECOGNITION: " + recognition)
            trans = translate(recognition, language_conf["lang_output"])
            print("TRANSLATION: " + trans.text)
            output = tx_to_sp(trans, language_conf["lang_output"])
            play_sound(output)
    except KeyboardInterrupt:
        print("\nGood Bye!...")
        sys.exit(0)
