import misc.defaults as defaults


class Parameters:
    def __init__(self):
        self._max_video_width = defaults.MAX_VIDEO_WIDTH
        self._max_video_height = defaults.MAX_VIDEO_HEIGHT

        self._first_reference_frame_index = defaults.FIRST_REFERENCE_FRAME_INDEX
        self._blur_size = defaults.BLUR_SIZE
        self._delta_threshold = defaults.DELTA_THRESHOLD
        self._minimal_move_area = defaults.MINIMAL_MOVE_AREA
        self._dilation_iterations = defaults.DILATION_ITERATIONS
        self._reference_frame_refresh_frequency = defaults.REFERENCE_FRAME_REFRESH_FREQUENCY

        self._use_running_average = False
        self._running_avg_alpha = defaults.RUNNING_AVG_ALPHA
        self._running_avg_start_frame_number = defaults.RUNNING_AVG_START_FRAME_NUMBER

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
    def first_reference_frame_index(self):
        return self._first_reference_frame_index

    @first_reference_frame_index.setter
    def first_reference_frame_index(self, index):
        self._first_reference_frame_index = index

    @property
    def blur_size(self):
        return self._blur_size

    @blur_size.setter
    def blur_size(self, blur_size):
        self._blur_size = blur_size

    @property
    def delta_threshold(self):
        return self._delta_threshold

    @delta_threshold.setter
    def delta_threshold(self, delta_threshold):
        self._delta_threshold = delta_threshold

    @property
    def minimal_move_area(self):
        return self._minimal_move_area

    @minimal_move_area.setter
    def minimal_move_area(self, minimal_move_area):
        self._minimal_move_area = minimal_move_area

    @property
    def dilation_iterations(self):
        return self._dilation_iterations

    @dilation_iterations.setter
    def dilation_iterations(self, dilation_iterations):
        self._dilation_iterations = dilation_iterations

    @property
    def reference_frame_refresh_frequency(self):
        return self._reference_frame_refresh_frequency

    @reference_frame_refresh_frequency.setter
    def reference_frame_refresh_frequency(self, frequency):
        self._reference_frame_refresh_frequency = frequency

    @property
    def use_running_average(self):
        return self._use_running_average

    @use_running_average.setter
    def use_running_average(self, use_running_average):
        self._use_running_average = use_running_average

    @property
    def running_avg_alpha(self):
        return self._running_avg_alpha

    @running_avg_alpha.setter
    def running_avg_alpha(self, running_avg_alpha):
        self._running_avg_alpha = running_avg_alpha

    @property
    def running_avg_start_frame_number(self):
        return self._running_avg_start_frame_number

    @running_avg_start_frame_number.setter
    def running_avg_start_frame_number(self, number):
        self._running_avg_start_frame_number = number
