"""Getting Started Example for Python 2.7+/3.3+"""
import boto3
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
import PyPDF2 as pdf2
from tkinter import *
from tkinter.filedialog import askopenfilename as of
from tkinter.filedialog import asksaveasfilename as sf
from tkinter.ttk import Combobox, Separator
import pygame

mixer = ""
filename = ""
pdf_text = ""


def play_audio():
    voice = combo0.get()
    text = combo1.get()
    play_audio_file(voice, text, "play")


def play_file(button):
    if button["text"] == "Play":
        button["text"] = "Pause"
        button["bg"] = "red"
        pygame.mixer.music.play()
    else:
        button["text"] = "Play"
        button["bg"] = "green"
        pygame.mixer.music.pause()


def play_audio_file(voice, text, mode):
    try:
        # Request speech synthesis
        response = polly.synthesize_speech(Text=text, OutputFormat="mp3",
                                            VoiceId=voice)
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            if mode == "play":
                output = os.path.join(gettempdir(), "speech.mp3")
            else:
                output = sf(defaultextension='.mp3', filetypes=[("mp3 files", '*.mp3')], initialdir='./',
                            title="Choose filename")
            try:
            # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)

    # Play the audio using the platform's default player
    if sys.platform == "win32":
        os.startfile(output)
    else:
        # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, output])


def convert_pdf():
    global filename, pdf_text
    filename = of(filetypes=[("PDF Files", "*.pdf")])
    print(f"filename is {filename}")
    pdf = pdf2.PdfReader(filename)
    print(f"{filename} has {len(pdf.pages)} pages.")
    for page in pdf.pages:
        pdf_text += page.extract_text()
    voice = combo0.get()
    play_audio_file(voice, pdf_text, "save")

# Create simple gui for opening a pdf, converting it to speech, and playing the speech file.


window = Tk()
window.geometry("465x340")
label0 = Label(window, text="PDF To Audio Converter", fg="#38a852", font=("Calibri", 24, "normal"))
label0.grid(row=0, column=0, columnspan=3, padx=26, pady=26)
label1 = Label(window, text="Choose Voice", fg="#232323", font=("Helvetica", 16, "normal"))
label1.grid(row=1, column=0, columnspan=3, padx=26, pady=26)
combo0 = Combobox(window, state="readonly", width=12, values=["Ivy", "Joanna", "Kendra",
                                        "Kimberly", "Salli", "Joey", "Justin", "Matthew"])
combo0.grid(row=2, column=0, padx=15, pady=15)
combo0.current(0)
button0 = Button(window, text='Sample Voice', width=14, bg='green', fg='black', command=play_audio)
button0.grid(row=2, column=1, padx=15, pady=15)
combo1 = Combobox(window, state="readonly", width=12, values=["Billions and billions and billions", "It is what it is",
                                "You wouldn't like me when I'm angry", "Is that your final answer"])
combo1.grid(row=2, column=2, padx=15, pady=15)
combo1.current(0)
# button1 = Button(window, text="Play Pdf", command=convert_pdf)
# button1.grid(row=4, column=0, columnspan=3, padx=15, pady=15)
# button2 = Button(window, text="Create Audio File", command=make_audio)
# button2.grid(row=4, column=2, padx=15, pady=15)
button3 = Button(window, text="Convert Pdf", fg="#38a852", font=("Calibri", 20, "normal"), command=convert_pdf)
button3.grid(row=4, column=0, columnspan=3, padx=26, pady=26)
# field0 = Entry(window, width=20, font=("Courier", 12, "normal"))
# field0.grid(row=5, column=0, columnspan=3, padx=15, pady=15)
# button4 = Button(window, text="Play File", command=play_audio)
# button4.grid(row=6, column=0, columnspan=3, padx=15, pady=20)

# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="cambium")
polly = session.client("polly")

window.mainloop()


