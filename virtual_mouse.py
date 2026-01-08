import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import urllib.request
import os
import time

frame_count = 0

prev_x, prev_y = 0, 0
smooth_factor = 4
last_click_time = 0
click_gap = 0.35

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

pyautogui.FAILSAFE = False
dragging = False

MODEL_PATH = "hand_landmarker.task"

# --------- Download model if missing ----------
if not os.path.exists(MODEL_PATH):
    print("Downloading hand model...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("Download complete.")

# --------- Create detector ----------
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

screen_w, screen_h = pyautogui.size()

mouse_enabled = False   # <-- NEW

def count_fingers(hand):
    # Simple rule: if tip is above its base → finger is open
    open_fingers = 0
    finger_tips = [8, 12, 16, 20]
    finger_bases = [6, 10, 14, 18]

    for tip, base in zip(finger_tips, finger_bases):
        if hand[tip].y < hand[base].y:
            open_fingers += 1

    return open_fingers


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    result = detector.detect(mp_image)

    if result.hand_landmarks:
        hand = result.hand_landmarks[0]

        # ---- TOGGLE MOUSE MODE ----
        fingers = count_fingers(hand)

        # Open palm → enable
        if fingers >= 3:
            mouse_enabled = True

        # Fist → disable
        if fingers == 0:
            mouse_enabled = False
            pyautogui.mouseUp()

        status = "ENABLED" if mouse_enabled else "DISABLED"
        color = (0, 255, 0) if mouse_enabled else (0, 0, 255)
        cv2.putText(frame, f"MOUSE: {status}", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Stop here if mouse is OFF
        if not mouse_enabled:
            cv2.imshow("Virtual Mouse", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            continue

        index_x, index_y = hand[8].x, hand[8].y
        thumb_x, thumb_y = hand[4].x, hand[4].y

        screen_x = int(index_x * screen_w)
        screen_y = int(index_y * screen_h)

        # -------- CURSOR SMOOTHING --------
        prev_x = prev_x + (screen_x - prev_x) / smooth_factor
        prev_y = prev_y + (screen_y - prev_y) / smooth_factor

        if abs(screen_x - prev_x) >= 3 or abs(screen_y - prev_y) >= 3:
            pyautogui.moveTo(prev_x, prev_y, duration=0)

        cx = int(index_x * frame.shape[1])
        cy = int(index_y * frame.shape[0])
        cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

        distance = ((index_x - thumb_x) ** 2 + (index_y - thumb_y) ** 2) ** 0.5

        middle_x, middle_y = hand[12].x, hand[12].y
        right_dist = ((middle_x - thumb_x) ** 2 + (middle_y - thumb_y) ** 2) ** 0.5

        if right_dist < 0.07:
            pyautogui.rightClick()
            pyautogui.sleep(0.25)

        if distance < 0.045:
            now = time.time()
            if now - last_click_time < click_gap:
                pyautogui.doubleClick()
                time.sleep(0.25)
            else:
                pyautogui.click()
                time.sleep(0.15)
            last_click_time = now

        drag_threshold = 0.035
        if distance < drag_threshold:
            pyautogui.mouseDown()
        else:
            pyautogui.mouseUp()

        scroll_min = 0.045
        scroll_max = 0.11

        if scroll_min < distance < scroll_max:
            scroll_speed = int((0.5 - index_y) * 60)
            if scroll_speed > 2:
                pyautogui.scroll(40)
            elif scroll_speed < -2:
                pyautogui.scroll(-40)

    cv2.imshow("Virtual Mouse", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()



#Move cursor,  Left click,  Double click,  Right click,  Drag & drop ,Scroll, Enable / disable mouse with hand gestures

#Start Control: 🖐️ Show open palm

#🖱️ Move Cursor:☝️ Move index finger

#👆 Click: 🤏 Pinch thumb + index

#🖱️ Right Click:🤏 Thumb + middle finger

#🖱️ Drag:🤏 Hold pinch

#📜 Scroll:🤏 Slight pinch + move up/down

# ⏸ Stop Control:✊ Make fist