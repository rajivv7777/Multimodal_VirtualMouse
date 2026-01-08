import cv2
import mediapipe as mp
import pyautogui
import time

pyautogui.FAILSAFE = False

mp_face = mp.solutions.face_mesh
cap = cv2.VideoCapture(0)

screen_w, screen_h = pyautogui.size()

smooth_x, smooth_y = 0, 0
alpha = 0.18     # smoothing factor (lower = smoother)

# --- calibration ---
calibrated = False
center_x = 0
center_y = 0
dead_zone = 25    # pixels tolerance around center
sensitivity = 1.8 # how strong the head movement controls cursor

with mp_face.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face:

    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = face.process(rgb)

        if result.multi_face_landmarks:
            lm = result.multi_face_landmarks[0]
            nose = lm.landmark[1]

            px = int(nose.x * w)
            py = int(nose.y * h)

            cv2.circle(frame, (px, py), 7, (0, 255, 0), -1)

            # -------- CALIBRATION --------
            if not calibrated:
                cv2.putText(frame, "Keep head still... calibrating",
                            (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                            (0, 255, 255), 2)

                if time.time() - start_time > 1.2:
                    center_x = px
                    center_y = py
                    calibrated = True

                cv2.imshow("Head Mouse", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
                continue

            # draw center reference
            cv2.circle(frame, (center_x, center_y), 6, (255, 0, 0), 2)

            dx = px - center_x
            dy = py - center_y

            # -------- DEAD ZONE --------
            if abs(dx) < dead_zone:
                dx = 0
            if abs(dy) < dead_zone:
                dy = 0

            target_x = screen_w // 2 + dx * sensitivity
            target_y = screen_h // 2 + dy * sensitivity

            # smoothing
            smooth_x = smooth_x + alpha * (target_x - smooth_x)
            smooth_y = smooth_y + alpha * (target_y - smooth_y)

            pyautogui.moveTo(smooth_x, smooth_y)

        cv2.putText(frame, "ESC to quit", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Head Mouse", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
