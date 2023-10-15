import cv2
import mediapipe as mp
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# 손 인식 및 볼륨 조절 기능
def hand_volume_control():
    cap = cv2.VideoCapture(0)
    mp_hands = mp.solutions.hands.Hands()
    volume_range = (-65.25, 0)  # 볼륨 범위 설정

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]

                thumb_x, thumb_y = int(thumb_tip.x * width), int(thumb_tip.y * height)
                index_x, index_y = int(index_tip.x * width), int(index_tip.y * height)

                distance = math.sqrt((thumb_x - index_x) ** 2 + (thumb_y - index_y) ** 2)

                # 볼륨 조절
                volume_value = np.interp(distance, [0, width], volume_range)
                volume.SetMasterVolumeLevel(volume_value, None)

                # 볼륨 바 그리기
                cv2.rectangle(frame, (10, 60), (30, int(height - 10)), (0, 255, 0), 2)
                volume_bar_height = int(np.interp(volume_value, volume_range, [height - 10, 60]))
                cv2.rectangle(frame, (10, volume_bar_height), (30, int(height - 10)), (0, 255, 0), cv2.FILLED)

                # 화면에 손가락 거리 그리기
                cv2.putText(frame, f"Distance: {int(distance)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 0), 2)

        cv2.imshow('Hand Volume Control', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# 메인 함수
if __name__ == '__main__':
    hand_volume_control()