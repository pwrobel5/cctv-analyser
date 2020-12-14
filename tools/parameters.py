import misc.defaults as defaults
from tools.subtractors import BgSubtractorType


class Parameters:
    def __init__(self):
        self._max_video_width = defaults.MAX_VIDEO_WIDTH
        self._max_video_height = defaults.MAX_VIDEO_HEIGHT

        self._blur_size = defaults.BLUR_SIZE
        self._minimal_move_area = defaults.MINIMAL_MOVE_AREA
        self._bg_subtractor = defaults.BG_SUBTRACTOR

        self._begin_with_sigmadelta = True
        self._sigmadelta_frames = defaults.SIGMADELTA_FRAMES

        self._use_threshold = True
        self._delta_threshold = defaults.DELTA_THRESHOLD
        self._dilation_iterations = defaults.DILATION_ITERATIONS

        self._max_contours = defaults.MAX_CONTOURS
        self._minimal_move_frames = defaults.MINIMAL_MOVE_FRAMES
        self._max_break_length = defaults.MAX_BREAK_LENGTH

        self._object_detection_interval = defaults.OBJECT_DETECTION_INTERVAL

        self._callbacks = {property_name: [] for property_name, _ in vars(self).items()}

    def add_callback(self, property_name, callback):
        self._callbacks[property_name].append(callback)

    def __run_callbacks(self, property_name):
        for callback in self._callbacks[property_name]:
            callback()

    @property
    def max_video_width(self):
        return self._max_video_width

    @max_video_width.setter
    def max_video_width(self, max_video_width):
        self._max_video_width = max_video_width
        self.__run_callbacks("_max_video_width")

    @property
    def max_video_height(self):
        return self._max_video_height

    @max_video_height.setter
    def max_video_height(self, max_video_height):
        self._max_video_height = max_video_height
        self.__run_callbacks("_max_video_height")

    @property
    def blur_size(self):
        return self._blur_size

    @blur_size.setter
    def blur_size(self, blur_size):
        self._blur_size = blur_size

    @property
    def minimal_move_area(self):
        return self._minimal_move_area

    @minimal_move_area.setter
    def minimal_move_area(self, minimal_move_area):
        self._minimal_move_area = minimal_move_area

    @property
    def bg_subtractor(self):
        return self._bg_subtractor.name

    @bg_subtractor.setter
    def bg_subtractor(self, bg_subtractor):
        self._bg_subtractor = BgSubtractorType[bg_subtractor]

    @property
    def bg_subtractor_enum(self):
        return self._bg_subtractor

    @property
    def begin_with_sigmadelta(self):
        return self._begin_with_sigmadelta

    @begin_with_sigmadelta.setter
    def begin_with_sigmadelta(self, begin_with_sigmadelta):
        self._begin_with_sigmadelta = begin_with_sigmadelta

    @property
    def sigmadelta_frames(self):
        return self._sigmadelta_frames

    @sigmadelta_frames.setter
    def sigmadelta_frames(self, sigmadelta_frames):
        self._sigmadelta_frames = sigmadelta_frames

    @property
    def use_threshold(self):
        return self._use_threshold

    @use_threshold.setter
    def use_threshold(self, use_threshold):
        self._use_threshold = use_threshold

    @property
    def delta_threshold(self):
        return self._delta_threshold

    @delta_threshold.setter
    def delta_threshold(self, delta_threshold):
        self._delta_threshold = delta_threshold

    @property
    def dilation_iterations(self):
        return self._dilation_iterations

    @dilation_iterations.setter
    def dilation_iterations(self, dilation_iterations):
        self._dilation_iterations = dilation_iterations

    @property
    def max_contours(self):
        return self._max_contours

    @max_contours.setter
    def max_contours(self, max_contours):
        self._max_contours = max_contours

    @property
    def minimal_move_frames(self):
        return self._minimal_move_frames

    @minimal_move_frames.setter
    def minimal_move_frames(self, minimal_move_frames):
        self._minimal_move_frames = minimal_move_frames

    @property
    def max_break_length(self):
        return self._max_break_length

    @max_break_length.setter
    def max_break_length(self, max_break_length):
        self._max_break_length = max_break_length

    @property
    def object_detection_interval(self):
        return self._object_detection_interval

    @object_detection_interval.setter
    def object_detection_interval(self, interval):
        self._object_detection_interval = interval
