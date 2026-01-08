import speech_recognition as sr
import pyautogui
import time
import os
import subprocess
import pathlib

r = sr.Recognizer()
pyautogui.FAILSAFE = False

APP_CACHE = {}
listening_enabled = True

def search_app(app_name):
    """
    Search Windows for an application exe / shortcut.
    Returns full path if found, otherwise None.
    """

    app_name = app_name.lower().replace(".exe", "").strip()

    search_paths = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        str(pathlib.Path.home() / "Desktop"),
        str(pathlib.Path.home() / "AppData\\Local\\Programs"),
        r"C:\Windows",
    ]

    # check cache first
    if app_name in APP_CACHE:
        return APP_CACHE[app_name]

    for base in search_paths:
        for root, dirs, files in os.walk(base):
            for f in files:
                name = f.lower()

                if app_name in name and (name.endswith(".exe") or name.endswith(".lnk")):
                    full_path = os.path.join(root, f)
                    APP_CACHE[app_name] = full_path
                    return full_path

    return None


print("\n Voice control ON")
print("Say things like:")
print("click | double click | right click")
print("scroll up | scroll down")
print("open chrome | open notepad | open vlc")
print("open photoshop | open eclipse | open spotify (anything)")
print("minimize window | maximize window | close window")
print("copy | paste | select all")
print("pause listening | start listening")
print("type hello world")
print("stop / exit\n")

while True:
    try:
        with sr.Microphone() as source:

            # ---------------- NEW FAST SETTINGS ----------------
            r.dynamic_energy_threshold = False
            r.energy_threshold = 320      # increase if still slow: 400–600

            # keep your original line (not deleted)
            r.adjust_for_ambient_noise(source, duration=0.4)

            print("Listening...")

            # ----- ORIGINAL -----
            # audio = r.listen(source, phrase_time_limit=4)

            # ----- NEW Faster Listening (added) -----
            audio = r.listen(
                source,
                timeout=2,            # stop waiting if no speech starts
                phrase_time_limit=4   # max speaking time
            )

        command = r.recognize_google(audio).lower()
        print("You said:", command)

        # ----------------- PAUSE / RESUME -----------------
        if "pause listening" in command or "stop listening" in command:
            listening_enabled = False
            print("⏸ Paused — say: start listening")
            continue

        if "start listening" in command or "resume listening" in command:
            listening_enabled = True
            print(" Listening resumed")
            continue

        # Ignore all commands while paused
        if not listening_enabled:
            continue

        # ----------------- EXIT -----------------
        if "stop" in command or "exit" in command or "quit" in command:
            print("Stopping voice control…")
            break

        # ----------------- MOUSE -----------------
        if "double click" in command:
            pyautogui.doubleClick()

        elif "right click" in command:
            pyautogui.rightClick()

        elif "click" in command:
            pyautogui.click()

        # ----------------- SCROLL -----------------
        elif "scroll up" in command:
            pyautogui.scroll(300)

        elif "scroll down" in command:
            pyautogui.scroll(-300)

        # ----------------- MOVE CURSOR -----------------
        elif "move up" in command:
            pyautogui.moveRel(0, -80)

        elif "move down" in command:
            pyautogui.moveRel(0, 80)

        elif "move left" in command:
            pyautogui.moveRel(-80, 0)

        elif "move right" in command:
            pyautogui.moveRel(80, 0)

        # ----------------- OPEN ANY APP -----------------
        elif command.startswith("open "):
            app = command.replace("open ", "").strip()

            print(f"Searching for: {app} ...")
            path = search_app(app)

            if path:
                print("Found:", path)
                try:
                    subprocess.Popen(path)
                    print("Opening", app)
                except Exception as e:
                    print("Could not open app:", e)
            else:
                print("Couldn't find that app on this PC")

        # ----------------- WINDOWS / SYSTEM -----------------
        elif "maximize window" in command:
            pyautogui.hotkey("win", "up")

        elif "minimize window" in command:
            pyautogui.hotkey("win", "down")

        elif "close window" in command:
            pyautogui.hotkey("alt", "f4")

        # ----------------- KEYBOARD SHORTCUTS -----------------
        elif "copy" in command:
            pyautogui.hotkey("ctrl", "c")

        elif "paste" in command:
            pyautogui.hotkey("ctrl", "v")

        elif "select all" in command:
            pyautogui.hotkey("ctrl", "a")

        # ----------------- TYPE TEXT -----------------
        elif command.startswith("type "):
            text = command.replace("type ", "")
            pyautogui.typewrite(text, interval=0.05)

        time.sleep(0.2)

    except sr.WaitTimeoutError:
        print("⏱️ No voice detected — retrying…")
        continue

    except sr.UnknownValueError:
        pass

    except KeyboardInterrupt:
        break

print("Voice control stopped.")



#SYSTEM / VOICE CONTROL
    #pause listening
    #stop listening
    #start listening
    #resume listening
    #stop
    #exit
    #quit

# MOUSE ACTIONS
    #click
    #double click
    #right click

# SCROLL
    #scroll up
    #scroll down

# MOVE CURSOR
    #move up
    #move down
    #move left
    #move right

# OPEN ANY APP (SEARCH & OPEN)
    #open chrome
    #open notepad , etc.

# WINDOWS / SYSTEM
    #close window (works like pressing Alt + F4)

# KEYBOARD SHORTCUTS
    #copy
    #paste
    #select all

# TYPE ANY TEXT
    #type "xyz....."
