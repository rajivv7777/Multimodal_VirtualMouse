import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import speech_recognition as sr
import threading
import subprocess
import os
import pathlib
import time
import urllib.request

# ================= GLOBAL FLAGS =================
mouse_enabled = False
voice_enabled = True
running = True

pyautogui.FAILSAFE = False
screen_w, screen_h = pyautogui.size()

# ================= VOICE SETUP =================
r = sr.Recognizer()
r.energy_threshold = 300
r.dynamic_energy_threshold = True

APP_CACHE = {}

# ================= APP SEARCH =================
def search_app(app_name):
    app_name = app_name.lower().replace(".exe", "").strip()

    if app_name in APP_CACHE:
        return APP_CACHE[app_name]

    search_paths = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        str(pathlib.Path.home() / "Desktop"),
        str(pathlib.Path.home() / "AppData\\Local\\Programs"),
        r"C:\Windows",
    ]

    for base in search_paths:
        for root, _, files in os.walk(base):
            for f in files:
                if app_name in f.lower() and (f.endswith(".exe") or f.endswith(".lnk")):
                    path = os.path.join(root, f)
                    APP_CACHE[app_name] = path
                    return path
    return None

# ================= VOICE THREAD =================
def voice_control():
    global voice_enabled, running

    print("\n🎤 Voice Control ON")
    print("Commands:")
    print("open <app> | close window | minimize window | maximize window")
    print("copy | paste | select all")
    print("pause listening | start listening")
    print("stop / exit\n")

    while running:
        try:
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=3, phrase_time_limit=3)

            command = r.recognize_google(audio).lower()
            print("🎙️", command)

            if "pause listening" in command:
                voice_enabled = False
                print("⏸ Voice paused")
                continue

            if "start listening" in command:
                voice_enabled = True
                print("▶ Voice resumed")
                continue

            if not voice_enabled:
                continue

            if "stop" in command or "exit" in command or "quit" in command:
                running = False
                break

            if command.startswith("open "):
                app = command.replace("open ", "")
                path = search_app(app)
                if path:
                    subprocess.Popen(path)
                else:
                    print("App not found")

            elif "close window" in command:
                pyautogui.hotkey("alt", "f4")

            elif "minimize window" in command:
                pyautogui.hotkey("win", "down")

            elif "maximize window" in command:
                pyautogui.hotkey("win", "up")

            elif "copy" in command:
                pyautogui.hotkey("ctrl", "c")

            elif "paste" in command:
                pyautogui.hotkey("ctrl", "v")

            elif "select all" in command:
                pyautogui.hotkey("ctrl", "a")

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print("Voice error:", e)

# ================= HAND SETUP =================
MODEL_PATH = "hand_landmarker.task"
if not os.path.exists(MODEL_PATH):
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        MODEL_PATH
    )

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

detector = vision.HandLandmarker.create_from_options(
    vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
        num_hands=1
    )
)

def count_fingers(hand):
    tips = [8, 12, 16, 20]
    bases = [6, 10, 14, 18]
    return sum(hand[t].y < hand[b].y for t, b in zip(tips, bases))

# ================= HAND THREAD =================
def hand_control():
    global mouse_enabled, running

    cap = cv2.VideoCapture(0)
    prev_x, prev_y = 0, 0
    smooth = 4

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = detector.detect(mp_image)

        if result.hand_landmarks:
            hand = result.hand_landmarks[0]
            fingers = count_fingers(hand)

            if fingers >= 3:
                mouse_enabled = True
            if fingers == 0:
                mouse_enabled = False
                pyautogui.mouseUp()

            status = "ENABLED" if mouse_enabled else "DISABLED"
            cv2.putText(frame, f"MOUSE: {status}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0) if mouse_enabled else (0, 0, 255), 2)

            if mouse_enabled:
                ix, iy = hand[8].x, hand[8].y
                sx, sy = int(ix * screen_w), int(iy * screen_h)

                prev_x += (sx - prev_x) / smooth
                prev_y += (sy - prev_y) / smooth

                pyautogui.moveTo(prev_x, prev_y, duration=0)

                tx, ty = hand[4].x, hand[4].y
                dist = ((ix - tx)**2 + (iy - ty)**2)**0.5

                if dist < 0.045:
                    pyautogui.click()
                    time.sleep(0.2)

        cv2.imshow("Virtual Mouse", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            running = False
            break

    cap.release()
    cv2.destroyAllWindows()

# ================= START THREADS =================
t1 = threading.Thread(target=hand_control)
t2 = threading.Thread(target=voice_control)

t1.start()
t2.start()

t1.join()
t2.join()

print("✅ System stopped")
