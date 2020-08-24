import tkinter.messagebox

import cv2


class VideoCapture:
    def __init__(self, video_source, parameters):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            tkinter.messagebox.showerror(title="Error", message="Unable to open video source " + video_source)
            raise ValueError("Unable to open video source", video_source)

        width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.resize = False
        self.parameters = parameters

        if width > self.parameters.max_video_width or height > self.parameters.max_video_height:
            self.resize = True

        self.width = min(width, self.parameters.max_video_width)
        self.height = min(height, self.parameters.max_video_height)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to RGB
                if self.resize:
                    frame = cv2.resize(frame, (self.parameters.max_video_width, self.parameters.max_video_height))

                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None
        else:
            return None, None

    def set_frame(self, val):
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, int(val))

    def get_frames_num(self):
        return self.vid.get(cv2.CAP_PROP_FRAME_COUNT)

    def get_fps(self):
        (opencv_version, _, _) = cv2.__version__.split(".")
        if int(opencv_version) < 3:
            return self.vid.get(cv2.cv.CV_CAP_PROP_FPS)
        else:
            return self.vid.get(cv2.CAP_PROP_FPS)

    def get_frame_by_index(self, index):
        self.set_frame(index)
        return self.get_frame()
