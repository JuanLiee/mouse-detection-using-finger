import cv2
import mediapipe as mp
import pyautogui
import win32api
import math
import time

mp_hands = mp.solutions.hands
screen_w, screen_h = pyautogui.size()
cap = cv2.VideoCapture(0)

prev_x, prev_y = 0, 0
alpha = 0.3

clicking = False
click_time = 0
scroll_mode = False
scroll_start_y = 0

with mp_hands.Hands(
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
) as hands:

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                lm = hand.landmark

                ix, iy = lm[8].x, lm[8].y
                tx, ty = lm[4].x, lm[4].y
                mx, my = lm[12].x, lm[12].y  # middle finger

                cx = int(ix * screen_w)
                cy = int(iy * screen_h)

                smooth_x = int(prev_x + (cx - prev_x) * alpha)
                smooth_y = int(prev_y + (cy - prev_y) * alpha)
                win32api.SetCursorPos((smooth_x, smooth_y))
                prev_x, prev_y = smooth_x, smooth_y

                pinch_dist = math.hypot(ix - tx, iy - ty)

                # CLICK
                if pinch_dist < 0.03:
                    if not clicking:
                        clicking = True
                        now = time.time()
                        if now - click_time < 0.4:
                            pyautogui.doubleClick()
                        else:
                            pyautogui.click()
                        click_time = now
                else:
                    clicking = False

                # SCROLL (pinch + middle finger up)
                if pinch_dist < 0.04 and my < iy:
                    if not scroll_mode:
                        scroll_mode = True
                        scroll_start_y = iy
                    else:
                        delta = scroll_start_y - iy
                        pyautogui.scroll(int(delta * 400))
                else:
                    scroll_mode = False

        if cv2.waitKey(1) == 27:  # ESC
            break

cap.release()
cv2.destroyAllWindows()
