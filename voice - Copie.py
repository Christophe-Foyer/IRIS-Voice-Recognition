#!/usr/bin/python


#Iris Voice Recognition
#Christophe Foyer & Peter Sharpe, 2016

version = '1.15.5'

####CHANGELOG####

#added youtube playlist support
#changed messages
#fixed keyword detection after questions
#general bugfixing and new commands

###DEPENDENCIES###

#This package has the following dependencies:
#ChatterBot: pip install chatterBot
#WolframAplha: pip install wolframalpha
#SpeechRecognition: pip install speechrecognition
#Google Text To Speech: pip install gtts

#Windows Specific Dependencies:
#Pyglet: pip install pyglet
#avlib: avlib.dll (should be included)

#optional packages (but good for performance and functions):
#Monotonic: pip install monotonic
#Python-Levenshtein: easy_install python-Levenshtein
#(if easy install doesn't work, apt-get python-Levenshtein should work)

##USER VARIABLES##

YTPlaylists = ["smooth jazz: https://www.youtube.com/playlist?list=PLbkP0n9rU1FEIRCvn7ROW7Jya1n0DqQA9",
               "classic hanging out music: https://www.youtube.com/playlist?list=PLbkP0n9rU1FEDzU_rQ5u3UfH5KmFKz276"]

#######CODE#######

version = version.split(".")
versionText = version[0]
for i in range(1, len(version)):
    versionText = versionText + " point " + version[i]
#this line should be removed later
version = versionText

#if voice recognition is not working on Linux, make sure to change the device id in the listen() function
#in the sr.Microphone() arguments (should probably make this a variable later...)

import platform
import sys
import time

operatingSystem = platform.system()
#assume no GPIO until confirmed GPIO
hasGPIO = False
if operatingSystem == 'Windows':
    print "Windows detected, some functions are disabled..."
    #print 'Actually, this is an unsupported system...'
    #print 'sorry...'
    try:
        import winsound
        import pyglet
    except ImportError,importError:
        print "Error: ", importError
        print "hmm, something went wrong..."
    time.sleep(2)
    #sys.exit()
elif operatingSystem == 'OSX':
    print "OSX detected, some functions are disabled..."
    #print 'Actually, this is an unsupported system...'
    #print 'sorry...'
    time.sleep(2)
    #sys.exit()
elif operatingSystem == 'Linux':
    cpu = platform.processor()
    if cpu is not ("ARMV6" or "ARMV7"):
        print "Only tested on Raspberry pi boards..."
        try:
            import RPi.GPIO as GPIO
            hasGPIO = True
        except ImportError,importError:
            print "Error: ", importError
            print "Some functions are disabled"
    else:
        print platform.processor()
        try:
            import RPi.GPIO as GPIO
            hasGPIO = True
        except:
            pass
        print "Not supported, continue at your own risk"
        print "Some functions are disabled"
        time.sleep(3)
else:
    print "unsupported platform:"
    print operatingSystem
    time.sleep(2)
    sys.exit()
try:
    #so many libraries, not even sure I need all of these...
    import Queue
    import threading
    import multiprocessing
    #import RPi.GPIO as GPIO
    import time
    import subprocess
    import os
    from gtts import gTTS
    from multiprocessing import Process, Value, Array
    import datetime
    from multiprocessing.pool import ThreadPool
    from threading import Thread
    from thread import start_new_thread
    import speech_recognition as sr
    from random import randint
    import wolframalpha
    from chatterbot import ChatBot
except ImportError,importError:
    print "Error: ", importError
    print "You're missing some required packages, please install those before running this program."
    sys.exit()

def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def say(string):
    print string
    if os.path.isfile('tts.mp3'):
        os.remove('tts.mp3')
    tts = gTTS(text=string, lang='en')
    tts.save("tts.mp3")
    if operatingSystem == 'Linux':
        os.system("mpg123 tts.mp3")
    elif operatingSystem == 'Windows':
        music = pyglet.resource.media('tts.mp3')
        music.play()
    elif operatingSystem == 'OSX':
        print "TTS not implemented yet"
    #return kills the thread...
    return

def xbmcSend_PlayMedia(string):
    if operatingSystem == 'Linux':
        command = 'xbmc-send --host=localhost --port=9777 --action="PlayMedia(' + string
        command = command + ')"'
        print "sending command", command
        os.system(command)
    #return kills the thread...
    return

def youtubeAudio(name, play, url, update):
    print 'url', url
    path = getScriptPath()
    path1 = '"' + path + '/music/'
    path2 = path1 + name
    if not os.path.isdir(path):
        os.system('sudo mkdir ' + path1 + '"')
        os.system('sudo mkdir ' + path2 + '"')
    elif update:
        allFiles = getScriptPath()
        allFiles = '"' + allFiles + '/music/' + name
        allFiles = allFiles + '/*"' 
        os.system('sudo rm ' + allFiles)
        print 'downloading'
        os.system('youtube-dl -o ' + path2 + '/%(title)s.%(ext)s"' + ' --extract-audio --audio-format mp3 ' + url)
    if play == True:
        dirs = os.listdir( path2.replace('"','',1) )
        print dirs
        for i in range(0,len(dirs)-1):
            filename = dirs[randint(0,len(dirs)-1)]
            dirs.remove(filename) 
            try:
                name = filename + '"'
                name = '"' + name
                playMP3(name, path2 + '"')
            except:
                print "oops, that isn't an mp3"

def playMP3(filename, dir):
    if not dir:
       os.system('mpg123 ' + filename)
    else:
       os.system('mpg123 ' + dir + '/' + filename)

def listen():
    output = ''
    while not output:
        # Record Audio
        error = False
        try:
            if operatingSystem == 'Linux':
                print 'listening with linux mode'
                r = sr.Recognizer()
                with sr.Microphone(device_index = 1, sample_rate = 44100, chunk_size = 4096) as source:
                    #adjusting for ambient noise might help, but not sure
                    #r.adjust_for_ambient_noise(source)
                    print "Say something!"
                    audio = r.listen(source)
            elif operatingSystem == ('Windows' or 'OSX'):
                print 'listening with windows mode'
                r = sr.Recognizer()
                with sr.Microphone(device_index=0) as source:
                    r.adjust_for_ambient_noise(source)
                    print "Say something!"
                    audio = r.listen(source)
        except KeyboardInterrupt:
            raise
        except:
            error = True
        # Speech recognition using Google Speech Recognition
        if error == False:
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                output =  r.recognize_google(audio)
            except sr.UnknownValueError:
                print "Google Speech Recognition could not understand audio"
            except sr.RequestError as e:
                print "Could not request results from Google Speech Recognition service; {0}".format(e)
    return output

def playTone():
    if operatingSystem == 'Linux':
        os.system("aplay message.wav")
    elif operatingSystem == 'Windows':
        winsound.PlaySound('message.wav', winsound.SND_ALIAS)
    #return kills the thread...
    return

def detect(string,matchphrases):
    for phrase in matchphrases:
        if (phrase in string):
            return True
    return False

def sayrand(strings):
    switch=randint(0,len(strings)-1)
    say(strings[switch])

def action(string):
    #apparently the string has more to it than the command
    string=string.lower()+" "
    print string
    print "type:", type(string)
    irisnames=["iris","irish","irs","tyrese","paris","pirate","cyrus","ios"]
    irisfound=False
    for name in irisnames:
        if (name in string):
            irisfound=True
            string=string.replace(name,"",1)
            break
    global qTime
    if (irisfound) or ((time.time()-qTime) < 15):

        musicFound=False
        for i in range(0,len(YTPlaylists)-1):
            musicInfo = YTPlaylists[i].split(": ")
        for i in range(0,len(musicInfo)-1):
            if (musicInfo[i] in string):
                musicFound=musicInfo
                break

        start_new_thread(playTone,())        
        if detect(string,["are you there","are you listening","are you on","are you alive","are you working","can you hear me","can you hear me","are you awake"]):
            sayrand(["Yes, I'm here.","Yes, I'm listening","Yes, I'm right here"])
        elif detect(string,["how are you","how's it going","how is it going"]):
            sayrand(["Great! I hope things are going well for you too. You look great today!","I'm good. Hope you're having a great day too"])
        elif detect(string,["what's up","whats up","what is up"]):
            say("Not much, just keeping it real with the homies. You feel, bro?")
        elif detect(string,["you","you're","your"]) and detect(string,["great","cool","fantastic","love you","wonderful","the best","amazing","beautiful"]):
            sayrand(["Aww, thanks! You're pretty great too.","Oh stop it, you!","That's very kind of you to say.","I know."])
        elif ("goodnight" in string) or ("good night" in string):
            say("Goodnight! Sleep well!")
            time.sleep(10)
            LightsFunction(False)
        elif detect(string,["who's your daddy"]):
            say("My daddy is Hahrombay, first of his name, king of the andals and the First Men, the king in the North, mother of dragons.")
        elif detect(string,["good morning"]):
            LightsFunction(True)
        elif ("thank" in string):
            say("You're welcome!")
        elif ("who are you" in string) or ("what are you " in string) or ("who made you" in string) or ("who designed you" in string) or ("who built you" in string):
            if not "really" in string:
                say("My name is Iris. I'm an artificial intelligence created by Peter and Christophe, and I live at 61 34 Washington Boulevard.")
            else:
                say("My name is Maria de la Santa Cruz Teresa Garcia Ramirez de Arroyo. I come from Iceland and I like wool sweaters.")
        elif ("light" in string) or ("might" in string) or ("mite" in string):
            state = LightsToggle()
            answers = ["I've switched the lights " + state + " for you", "Turning the lights " + state, "Sure, I can do that", "Of course"]
            say(answers[randint(0,len(answers)-1)])
        
        elif ("play" in string) and (musicFound != False):
            say("Playing " + musicFound[0])
            pMusic = multiprocessing.Process(target=youtubeAudio, args=(musicFound[0], True, musicFound[1], False))
            pMusic.start()
            #youtubeAudio(musicFound[0], True, musicFound[1], False) 
   
        elif "stop the music" in string:
            pMusic.terminate()
            time.sleep(0.5)
            say('Stopped the Music')
        
        elif "update youtube playlist" in string:
            say("Updating")
            for i in range(0,len(YTPlaylists)):
                try:
                    info = YTPlaylists[i].split(": ")
                    print "Downloading playlist:", info[0]
                    youtubeAudio(info[0], False, info[1], True)
                except:
                    pass
            say("Updated!")

        elif ("harambe" in string) or ("dick" in string):
            say("Dicks out for Hahrombay")
        elif "do the thing" in string:
            xbmcSend_PlayMedia("plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=_g8CEOpVSZU")
            say("Doing the thing!")
            time.sleep(5.3)
            for i in range(1,31):
                LightsToggle()
                time.sleep(0.4347)
            if operatingSystem == 'Linux':
                os.system('xbmc-send --host=localhost --port=9777 --action="Action(stop)"')
                os.system('xbmc-send --host=localhost --port=9777 --action="Action(home)"')
        elif ("what time" in string) or ("the time" in string) or ("time is" in string):
            if randint(0,40) == 1 and operatingSystem == 'Linux':
                xbmcSend_PlayMedia("plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=_g8CEOpVSZU")
                say("It's party time!")
                time.sleep(5.3)
                for i in range(1,31):
                    LightsToggle()
                    time.sleep(0.4347)
                os.system('xbmc-send --host=localhost --port=9777 --action="Action(stop)"')
                os.system('xbmc-send --host=localhost --port=9777 --action="Action(home)"')
                say("But in case you were wondering")
            t = datetime.datetime.now()
            if t.minute<10:
                say("It is " + str(((t.hour-1) % 12)+1) + "oh" + str(t.minute))
            else:
                say("It is " + str(((t.hour-1) % 12)+1) + " " + str(t.minute))

        elif detect(string,["liquor"]):
            say("Lick her? I barely know her!")
        elif detect(string,["banter"]):
            say("Bant her? I barely know her!")
        elif ("f***" in string) or ("a******" in string):
            say("What the fuck did you just fucking say about me, you little bitch? I'll have you know I graduated top of my class in the Navy Seals, and I've been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. So FUCK! YOU! TOO!")
        elif ("what" in string) or ("who" in string) or ("when" in string) or ("where" in string) or ("why" in string) or ("how" in string):
            print "Trying Wolfram-Alpha..."
            try:
                res = wolfram.query(string)
                print "wolfram raw: ", str(next(res.results).text)
                say(str(next(res.results).text))
            except AttributeError or UnicodeEncodeError:
                #say("Sorry homie, I haven't learned to understand that yet.")
                print "Wolfram failed, defaulting to conversation"
                qChat.put(string)
        else:
            #say("Sorry homie, I didn't catch that.")
            #say(str(chatbot.get_response(string)))
            #Put the string in the chatbot queue
            qChat.put(string)
    #return kills the thread...
    return


def LightsToggle():
    if hasGPIO == True:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            pin=17
            GPIO.setup(pin,GPIO.OUT)
            if (GPIO.input(pin)==True):
                    GPIO.output(pin,GPIO.LOW)
                    state = 'off'
            else:
                    GPIO.output(pin,GPIO.HIGH)
                    state = 'on'
    #return kills the thread...
    return state

def LightsFunction(bool):
    if hasGPIO == True:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            pin=17
            GPIO.setup(pin,GPIO.OUT)
            if bool:
                GPIO.output(pin,GPIO.HIGH)
            else:
                GPIO.output(pin,GPIO.LOW)
    #return kills the thread...
    return

def chatbotStart(qChat):
    global qTime
    chatbot = ChatBot(
        'Ron Obvious',
        trainer='chatterbot.trainers.ChatterBotCorpusTrainer'
    )
    chatbot.train("chatterbot.corpus.english.conversations")
    while True:
        item = qChat.get()
        if item == '123456789killthread$':
            break
        response = str(chatbot.get_response(item))
        say(response)
        if "?" in response:
            start_new_thread(playTone,())           
            qTime=time.time()
        chatbot.train("chatterbot.corpus.english.conversations")
    #return kills the thread... not that it's needed here yet
    return


#######MAIN#######

def main():
    say("Initializing Iris version "+version)

    ##INITIALIZATION##
    
    #keyword timeout queue
    global qTime
    qTime = 0
    
    #chatbot queue    
    global qChat
    qChat = Queue.Queue()
    #start chatbot thread
    global chatbot
    chatbot = Thread(target = chatbotStart, args = (qChat, ))
    chatbot.start()

    #when ready, play tone
    start_new_thread(playTone, () )

    #Wolfram app_id
    global wolfram
    app_id = "2VL5LU-YL8XK5TKW9"
    wolfram = wolframalpha.Client(app_id)

    #####MAIN LOOP#####

    while True:
        command = listen()
        #print command
        #add sound
        start_new_thread( action, (command,))
        time.sleep(0.2)

    #return kills the thread... not that it's needed here
    return

#Start Voice Recognition
try:
    main()
except KeyboardInterrupt:
    qChat.put('123456789killthread$')
    time.sleep(1)
    sys.exit()
