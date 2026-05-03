# Mediapipe + Video + Drawing
import mediapipe as mp
import cv2
import numpy as np
from .config import Config
from .engine import Engine
from line_profiler import profile

class Visualizer:
    '''Process a single frame'''
    def __init__(self, frame:np.ndarray, detection):
        self.frame = frame
        self.detection = detection

    def draw_landmarks(self)->np.ndarray:
        # just drawing the all fingers tips and central point(wrist)
        hlm = self.detection.hand_landmarks
        image = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
        H, W, _ = image.shape
        for i in range(len(hlm)):
            for j in range(0, 21, 4):
                tip = hlm[i][j]
                cv2.circle(image, (int(tip.x*W), int(tip.y*H)), 8, (219, 199, 145), -1)
        return image


class Model:
    '''Take Source file address to like a video. If Source parameter is not given,\n
    then By default, it opens live cam with your inbuilt webcam'''
    def __init__(self, Source=0):
        self.Model = "DetectionModel/Model/hand_landmarker.task"
        self.cam = cv2.VideoCapture(Source)
        self.BaseOptions = mp.tasks.BaseOptions
        self.HandLandMarker = mp.tasks.vision.HandLandmarker
        self.HandLandMarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        self.RunningMode = mp.tasks.vision.RunningMode
        self.Options = self.HandLandMarkerOptions(
            base_options = self.BaseOptions(model_asset_path = self.Model),
            num_hands = 2,
            running_mode = self.RunningMode.VIDEO
        )
        self.LandMarker = self.HandLandMarker.create_from_options(self.Options)
        self.direction = "Stable"
        self.FPS = self.cam.get(cv2.CAP_PROP_FPS)
        self.FrameIndex = 0

    @profile
    def video(self):
        engine = Engine()
        while True:
            status, frame = self.cam.read()
            if not status:
                break
            
            frame = cv2.resize(frame, (900,600))
            image = frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            timestamp_ms = int(self.FrameIndex*(1000/self.FPS))

            img = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

            # here a detection skip karna padega for cpu saving, alternate frame checking VVVV
            # VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
            Detection = self.LandMarker.detect_for_video(img, timestamp_ms)
            # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

            if Detection.handedness == [] and Detection.hand_landmarks == [] and Detection.hand_world_landmarks == []:
                self.FrameIndex += 1
                continue

            engine.update(Detection, self.FrameIndex)
            if self.FrameIndex % Config.FRAME_SKIP == 0:
                self.direction = engine.classifier()

            if Config.DEBUG_MODE:
                annoted_image = image
                if Config.VISUAL_MODE:
                    visualizer = Visualizer(frame,Detection)
                    annoted_image = visualizer.draw_landmarks()
                    
                cv2.putText(annoted_image, str(self.direction), (50,50), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0,0,255), 2)
                cv2.imshow("Output", annoted_image)
            else:
                cv2.putText(image, str(self.direction), (50,50), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0,0,255), 2)
                cv2.imshow("Output", image)

            if cv2.waitKey(1) & 0xff == ord('q'):
                break

            self.FrameIndex += 1
        
        cv2.destroyAllWindows()
        