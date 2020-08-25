import cv2
import numpy as np


class Analyser:
    def __init__(self, reference_frame, parameters):
        # TODO - what does this 0 mean?
        self._parameters = parameters
        self._reference_frame = cv2.GaussianBlur(reference_frame, (parameters.blur_size, parameters.blur_size), 0)
        self._running_average = np.float32(reference_frame)
        self._frame_counter = 0

    def analyse_frame(self, frame):
        text = "No motion"
        analysed_frame = cv2.GaussianBlur(frame, (self._parameters.blur_size, self._parameters.blur_size), 0)
        self._frame_counter += 1

        if self._parameters.use_running_average:
            if not self.__check_if_running_avg_has_proper_size(analysed_frame):
                self.__resize_running_average(analysed_frame)

            cv2.accumulateWeighted(analysed_frame, self._running_average, self._parameters.running_avg_alpha, None)
            frame_delta = cv2.subtract(self._running_average, analysed_frame, dtype=cv2.CV_32F)
            frame_delta = cv2.convertScaleAbs(frame_delta)
        else:
            if not self.__check_if_reference_frame_has_proper_size(analysed_frame):
                self.__resize_reference_frame(analysed_frame)
            frame_delta = cv2.absdiff(self._reference_frame, analysed_frame)
        frame_delta = cv2.cvtColor(frame_delta, cv2.COLOR_RGB2GRAY)
        threshold = cv2.threshold(frame_delta, self._parameters.delta_threshold, 255, cv2.THRESH_BINARY)[1]
        threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, None)
        threshold = cv2.dilate(threshold, None, iterations=self._parameters.dilation_iterations)

        contours = cv2.findContours(threshold.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        # length of contours and position of needed element to read is dependent on OpenCV version
        if len(contours) == 2:
            contours = contours[0]
        elif len(contours) == 3:
            contours = contours[1]
        else:
            print("Error")
            return None

        motion_detected = False

        for contour in contours:
            if cv2.contourArea(contour) < self._parameters.minimal_move_area:
                continue

            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Motion detected"
            motion_detected = True

        cv2.putText(frame, "Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)

        if not motion_detected and self._frame_counter >= self._parameters.reference_frame_refresh_frequency:
            self._reference_frame = analysed_frame
            self._frame_counter = 0
            print("Changed reference frame")

        return frame, motion_detected

    def __check_if_reference_frame_has_proper_size(self, current_frame):
        height, width, _ = current_frame.shape
        ref_height, ref_width, _ = self._reference_frame.shape

        if ref_height != height or ref_width != width:
            return False

        return True

    def __check_if_running_avg_has_proper_size(self, current_frame):
        height, width, _ = current_frame.shape
        ref_height, ref_width, _ = self._running_average.shape

        if ref_height != height or ref_width != width:
            return False

        return True

    def __resize_reference_frame(self, current_frame):
        width, height, _ = current_frame.shape
        self._reference_frame = cv2.resize(self._reference_frame, (height, width))

    def __resize_running_average(self, current_frame):
        width, height, _ = current_frame.shape
        self._running_average = cv2.resize(self._running_average, (height, width))

    @property
    def reference_frame(self):
        return self._reference_frame

    @reference_frame.setter
    def reference_frame(self, reference_frame):
        self._reference_frame = cv2.GaussianBlur(reference_frame,
                                                 (self._parameters.blur_size, self._parameters.blur_size), 0)
