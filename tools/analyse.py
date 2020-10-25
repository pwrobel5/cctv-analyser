import cv2
import numpy as np


class Analyser:
    def __init__(self, reference_frame, parameters, frames_to_average=None, bg_subtractor="KNN"):
        self._parameters = parameters
        self._reference_frame = self.__preprocess_frame(reference_frame)
        self._running_average = self.__calculate_average_frame(frames_to_average)
        self._frame_counter = 0
        if bg_subtractor == "KNN":
            self._background_subtractor = cv2.createBackgroundSubtractorKNN(detectShadows=False)
        else:
            self._background_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)

    def __calculate_average_frame(self, frames):
        if not frames:
            return None
        result = np.zeros(frames[0].shape, np.float)
        n_frames = len(frames)

        for frame in frames:
            result = result + frame / n_frames

        result = cv2.normalize(result, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        result = self.__preprocess_frame(result)
        return result

    def __preprocess_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # TODO - what does this 0 mean?
        frame = cv2.GaussianBlur(frame, (self._parameters.blur_size, self._parameters.blur_size), 0)
        return frame

    def analyse_frame(self, frame):
        text = "No motion"
        frame_copy = frame.copy()
        frame_copy = cv2.GaussianBlur(frame_copy, (self._parameters.blur_size, self._parameters.blur_size), 0)
        bg_mask = self._background_subtractor.apply(frame_copy)
        # cv2.imshow(frame, "aa")
        analysed_frame = self.__preprocess_frame(frame)
        self._frame_counter += 1

        if self._parameters.use_running_average:
            if not self.__check_if_running_avg_has_proper_size(analysed_frame):
                self.__resize_running_average(analysed_frame)

            cv2.accumulateWeighted(analysed_frame, self._running_average, self._parameters.running_avg_alpha, None)
            frame_delta = cv2.subtract(self._running_average, analysed_frame, dtype=cv2.CV_32F)
            frame_delta = cv2.convertScaleAbs(frame_delta)
            cv2.imshow("Running average", self._running_average / 255)
        else:
            if not self.__check_if_reference_frame_has_proper_size(analysed_frame):
                self.__resize_reference_frame(analysed_frame)
            frame_delta = cv2.absdiff(self._reference_frame, analysed_frame)
            cv2.imshow("Reference frame", self._reference_frame)
        # frame_delta = cv2.cvtColor(frame_delta, cv2.COLOR_RGB2GRAY)

        threshold = cv2.threshold(frame_delta, self._parameters.delta_threshold, 255, cv2.THRESH_BINARY)[1]
        threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, None)
        threshold = cv2.dilate(threshold, None, iterations=self._parameters.dilation_iterations)

        cv2.imshow("Threshold", threshold)
        cv2.imshow("Frame delta", frame_delta)

        bg_threshold = cv2.threshold(bg_mask, self._parameters.delta_threshold, 255, cv2.THRESH_BINARY)[1]

        contours = cv2.findContours(threshold.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        contours_bg = cv2.findContours(bg_threshold.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        # length of contours and position of needed element to read is dependent on OpenCV version
        if len(contours) == 2:
            contours = contours[0]
        elif len(contours) == 3:
            contours = contours[1]
        else:
            print("Error")
            return None

        if len(contours_bg) == 2:
            contours_bg = contours_bg[0]
        elif len(contours_bg) == 3:
            contours_bg = contours_bg[1]
        else:
            print("Error")
            return None

        """
        bg_text = "No motion"

       for contour_bg in contours_bg:
            if cv2.contourArea(contour_bg) < self._parameters.minimal_move_area:
                continue

            (x, y, w, h) = cv2.boundingRect(contour_bg)
            cv2.rectangle(bg_mask, (x,y), (x + w, y + h), (0, 255, 0), 2)
            bg_text = "Motion detected"

        cv2.putText(bg_mask, "Status: {}".format(bg_text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)"
        """

        cv2.imshow("After bg subtraction", bg_threshold)
        # OpenCV needs it to correctly show images for some reason
        # (https://stackoverflow.com/questions/21810452/cv2-imshow-command-doesnt-work-properly-in-opencv-python/50947231)
        #cv2.waitKey(1)

        motion_detected = False
        found_contours = len(contours_bg)
        contours_bg = list(filter(lambda cnt: cv2.contourArea(cnt) >= self._parameters.minimal_move_area, contours_bg))

        if found_contours < 500:
            for contour in contours_bg:
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Motion detected"
                motion_detected = True

        cv2.putText(frame, "Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)
        if motion_detected:
            print("Contours: ", found_contours)

        if not motion_detected and self._frame_counter >= self._parameters.reference_frame_refresh_frequency:
            self._reference_frame = analysed_frame
            self._frame_counter = 0
            print("Changed reference frame")

        cv2.imshow("Frame", frame)
        cv2.waitKey(1)

        return frame, motion_detected

    def __check_if_reference_frame_has_proper_size(self, current_frame):
        height, width = current_frame.shape
        ref_height, ref_width = self._reference_frame.shape

        if ref_height != height or ref_width != width:
            return False

        return True

    def __check_if_running_avg_has_proper_size(self, current_frame):
        height, width = current_frame.shape
        ref_height, ref_width = self._running_average.shape

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
