import cv2
import mediapipe as mp
import time

# --- FaceMesh setup ---
mp_face = mp.solutions.face_mesh
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# FPS helper
prev_time = 0

with mp_face.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face:

    while True:
        success, frame = cap.read()
        if not success:
            break

        # mirror
        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face.process(rgb)

        # draw landmarks
        if result.multi_face_landmarks:
            for lm in result.multi_face_landmarks:
                mp_draw.draw_landmarks(
                    frame,
                    lm,
                    mp_face.FACEMESH_TESSELATION
                )

        # show FPS (helps check lag)
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
        prev_time = curr_time

         # display fps
        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow("Head Tracking", frame)

        # ---- ESC to quit safely ----
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
