import cv2
import numpy as np


class VideoWriter:
    def __init__(self, width, height, path):
        self.shortcut_video_path = self.__set_output_path(path)
        self.width = width
        self.height = height
        self.writer = None
        self.__initialize_video_writer()

    def __set_output_path(self, path):
        return "./output.avi"

    def __initialize_video_writer(self):
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        self.writer = cv2.VideoWriter(self.shortcut_video_path, fourcc, 30, (int(self.width), int(self.height)), True)

    def add_frame(self, frame):
        #black = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #frame = np.zeros(shape=[int(self.width), int(self.height), 3], dtype=np.uint8)

        #cv2.putText(frame, "fdsggd", (100, 100- 5),
        #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (24,67,224), 2)
        self.writer.write(frame)
        #frame = np.zeros(shape=[int(self.width), int(self.height), 3], dtype=np.uint8)
        #self.writer.write(black)

    def add_black_frame(self, start, end, frame):
        #black = cv2.cvtColor(frame, cv2.COLOR_GRA)
        for i in range (1, 60):
            frame = np.zeros(shape=[int(self.height), int(self.width), 3], dtype=np.uint8)
            cv2.putText(frame, start + " - " + end, (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            self.writer.write(frame)

    def on_finish(self):
        self.writer.release()

    def write(self, frame):
        self.writer.write(frame)

    def release(self):
        print("RELEASED")
        self.writer.release()