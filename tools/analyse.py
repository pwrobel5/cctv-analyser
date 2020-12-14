from threading import Thread

import cv2
#import pybgs
import pybgs


from .subtractors import BgSubtractorType

SUBTRACTORS = {
    BgSubtractorType.KNN: cv2.createBackgroundSubtractorKNN,
    BgSubtractorType.ViBe: pybgs.ViBe,
    BgSubtractorType.SigmaDelta: pybgs.SigmaDelta,
    BgSubtractorType.AdaptiveSegmenter: pybgs.PixelBasedAdaptiveSegmenter
}

NO_MOVEMENT_INDEX = -1


class Analyser:
    def __init__(self, parameters, detector, show_preview=True):
        self._parameters = parameters
        self._frame_counter = 0
        self._background_subtractor = self.__initialize_bg_subtractor()

        self._movement_begin = NO_MOVEMENT_INDEX
        self._movement_end = NO_MOVEMENT_INDEX
        self._moving_frames = 0
        self._breaking_frames = 0
        self._motion_detected = False
        self._object_detector = detector
        self._frames_to_detect = []
        self._detection_threads = []

        self._show_preview = show_preview
    #     self.shortcut_video_path = "./output.avi"
    #     self.writer = None
    #     self.__initialize_video_writer()
    #
    # def __initialize_video_writer(self):
    #     fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    #     self.writer = cv2.VideoWriter(self.shortcut_video_path, fourcc, 30,
    #                              (480, 480), True)

    def __initialize_bg_subtractor(self):
        if self._parameters.begin_with_sigmadelta:
            return pybgs.SigmaDelta()
        else:
            return self.__create_bg_subtractor()

    def __create_bg_subtractor(self):
        bg_subtractor = self._parameters.bg_subtractor_enum
        subtractor_initializer = SUBTRACTORS.get(bg_subtractor, cv2.BackgroundSubtractorKNN)
        return subtractor_initializer()

    def analyse_frame(self, frame):
        return_frame_index = None
        self._frame_counter += 1
        self.__switch_subtractors_if_needed()
        bg_mask = self.__get_bg_mask(frame)

        if self._parameters.use_threshold:
            bg_threshold = self.__get_thresholded_mask(bg_mask)
        else:
            bg_threshold = bg_mask

        contours_bg = self.__get_contours(bg_threshold)
        found_contours = len(contours_bg)
        contours_bg = list(filter(lambda cnt: cv2.contourArea(cnt) >= self._parameters.minimal_move_area, contours_bg))

        if len(contours_bg) > 0 and found_contours < self._parameters.max_contours:
            self.__set_motion_counters()
            self.__mark_contours(contours_bg, frame)

            if self._moving_frames >= self._parameters.minimal_move_frames:
                self._motion_detected = True
                return_frame_index = self._movement_begin
        else:
            self.__set_break_counters()

            if self._breaking_frames >= self._parameters.max_break_length:
                print("STOP")
                return_frame_index = self._movement_end
                self.__unmark_motion()
                t = Thread(target=self._object_detector.detect_objects, args=(self._frames_to_detect,))
                t.start()
                self._detection_threads.append(t)
                self._frames_to_detect = []

        if self._motion_detected and self._moving_frames > self._parameters.max_break_length and \
                self._moving_frames % self._parameters.object_detection_interval == 0:
            self._frames_to_detect.append(frame)
            print("ADD")

        # if self._motion_detected:
        #     self.writer.write(frame)

        status = "Motion detected" if self._motion_detected else "No motion"
        cv2.putText(frame, "Status: {}".format(status), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)

        if self._show_preview:
            cv2.imshow("After bg subtraction", bg_threshold)
            cv2.imshow("Frame", frame)

            # OpenCV needs it to correctly show images for some reason
            # (https://stackoverflow.com/questions/21810452/cv2-imshow-command-doesnt-work-properly-in-opencv-python/50947231)
            cv2.waitKey(1)

        return frame, self._motion_detected, return_frame_index

    def __switch_subtractors_if_needed(self):
        if self._parameters.begin_with_sigmadelta and self._frame_counter == self._parameters.sigmadelta_frames:
            self._background_subtractor = self.__create_bg_subtractor()
            print("Switching algorithm...")

    def __get_bg_mask(self, frame):
        frame_copy = frame.copy()
        frame_copy = cv2.GaussianBlur(frame_copy, (self._parameters.blur_size, self._parameters.blur_size), 0)
        return self._background_subtractor.apply(frame_copy)

    def __get_thresholded_mask(self, bg_mask):
        bg_threshold = cv2.threshold(bg_mask, self._parameters.delta_threshold, 255, cv2.THRESH_BINARY)[1]
        bg_threshold = cv2.morphologyEx(bg_threshold, cv2.MORPH_OPEN, None)
        bg_threshold = cv2.dilate(bg_threshold, None, iterations=self._parameters.dilation_iterations)
        return bg_threshold

    @staticmethod
    def __get_contours(bg_threshold):
        contours_bg = cv2.findContours(bg_threshold.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        # length of contours and position of needed element to read is dependent on OpenCV version
        if len(contours_bg) == 2:
            contours_bg = contours_bg[0]
        elif len(contours_bg) == 3:
            contours_bg = contours_bg[1]
        else:
            print("Error")
            return None

        return contours_bg

    def __set_motion_counters(self):
        if self._movement_begin == NO_MOVEMENT_INDEX:
            self._movement_begin = self._frame_counter

        self._movement_end = self._frame_counter
        self._moving_frames += 1

    @staticmethod
    def __mark_contours(contours_bg, frame):
        for contour in contours_bg:
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    def __set_break_counters(self):
        if self._movement_begin != NO_MOVEMENT_INDEX:
            self._breaking_frames += 1

    def __unmark_motion(self):
        self._motion_detected = False
        self._movement_begin = NO_MOVEMENT_INDEX
        self._movement_end = NO_MOVEMENT_INDEX
        self._moving_frames = 0
        self._breaking_frames = 0

    @staticmethod
    def destroy_windows():
        cv2.destroyAllWindows()

    def wait_for_detection(self):
        for thread in self._detection_threads:
            thread.join()
