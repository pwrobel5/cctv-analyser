import cv2
import numpy as np
import yaml


class VideoWriter:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.writer = None
        self.shortcut_video_path = None

    def __set_output_path(self, path):
        with open("./analyse_stat.yaml") as stat_file:
            analysed_files = yaml.load(stat_file, Loader=yaml.FullLoader)
        index = analysed_files.get(path)
        path = path[0: path.rfind("."):] + "_shortcut_" + str(index) + ".avi"
        self.shortcut_video_path = path

    def initialize_video_writer(self, path):
        self.__set_output_path(path)
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        self.writer = cv2.VideoWriter(self.shortcut_video_path, fourcc, 30, (int(self.width), int(self.height)), True)

    def add_frame(self, frame):
        self.writer.write(frame)

    def add_black_frame(self, start, end, frame, is_date):
        if is_date:
            for i in range(1, 60):
                frame = np.zeros(shape=[int(self.height), int(self.width), 3], dtype=np.uint8)
                cv2.putText(frame, start + " - ", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.putText(frame, end, (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                self.writer.write(frame)
        else:
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
