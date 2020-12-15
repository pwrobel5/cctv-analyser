import cv2


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
        self.writer.write(frame)

    def on_finish(self):
        self.writer.release()

    def write(self, frame):
        self.writer.write(frame)

    def release(self):
        print("RELEASED")
        #self.writer.release()