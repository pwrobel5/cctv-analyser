from tools.object_detection import object_detector_video
import tkinter.filedialog as filedialog
from gui.video_capture import VideoCapture
from tools.parameters import Parameters
import tkinter as tk

video_source = None

def main():
    detector = object_detector_video.ObjectDetectorVideo()
    detector.upload_video("samples/sample.mp4")
    detector.detect_objects()


if __name__ == '__main__':
    main()


def browse():
    path = filedialog.askopenfilename()
    if path:
        try:
            global video_source
            _parameters = Parameters()
            _parameters.add_callback("_max_video_width", __update_canvas_size_without_video)
            _parameters.add_callback("_max_video_height", __update_canvas_size_without_video)
            video_source = VideoCapture(path, _parameters, __update_canvas_size_with_video)
        except ValueError:
            return

        __update_canvas_size_with_video()
        # self.delay = int(1000 / self.video_source.get_fps())  # 1000 to obtain delay in microseconds
        jump_to_video_beginning()


def __update_canvas_size_without_video(self):
    width = self._parameters.max_video_width
    height = self._parameters.max_video_height
    self.__update_canvas_size(width, height)