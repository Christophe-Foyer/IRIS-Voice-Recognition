# IRIS-Voice-Recognition

Voice recognition software written in python with cross-platform compatibility, but meant to be run on raspberry pi.
Lots of fun commands and easy customization (edit the action function to add more commands)
Machine learning using chatterbot for conversations.
OSMC integration

# Usage (Linux)

command: sudo python voice.py

# Usage (Windows)

run start.bat

# Dependencies

This package has the following dependencies:  
(FORMAT: %name%: %command to install%)

ChatterBot: pip install chatterBot  
WolframAplha: pip install wolframalpha  
SpeechRecognition: pip install speechrecognition  
Google Text To Speech: pip install gtts  
Mutagen: pip install mutagen  
Python-Daemon: pip install python-daemon

Windows Specific Dependencies:

Pyglet: pip install pyglet  
avlib: avlib.dll (should be included)

Optional packages (performance improvements):

Monotonic: pip install monotonic  
Python-Levenshtein: easy_install python-Levenshtein  
(if easy install doesn't work, apt-get python-Levenshtein should work)

# Regarding issues during installation:

The instructions for setup are not complete yet, if you run into any trouble, I will gladly provide you with assistance.
