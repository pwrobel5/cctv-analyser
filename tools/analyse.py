import cv2

"""
        to parametrize:
          first reference frame - maybe user could set which is correct?
          size of Gaussian smoothing
          eventual resizing - would make the process faster
          do we really need to convert image to grayscale?
          delta threshold - how much different from black must be area to consider it as a movement
          minimum area to detect motion
"""


class Analyser:
    def __init__(self, reference_frame, blur_size=21, move_threshold=25, dilation_iterations=2):
        reference_frame = cv2.cvtColor(reference_frame, cv2.COLOR_RGB2GRAY)
        # TODO - what does this 0 mean?
        self._reference_frame = cv2.GaussianBlur(reference_frame, (blur_size, blur_size), 0)
        self._minimal_area = 200
        self._blur_size = blur_size
        self._move_threshold = move_threshold
        self._dilation_iterations = dilation_iterations

    def analyse_frame(self, frame):
        text = "No motion"
        analysed_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        analysed_frame = cv2.GaussianBlur(analysed_frame, (self._blur_size, self._blur_size), 0)

        frame_delta = cv2.absdiff(self._reference_frame, analysed_frame)
        threshold = cv2.threshold(frame_delta, self._move_threshold, 255, cv2.THRESH_BINARY)[1]
        threshold = cv2.dilate(threshold, None, iterations=self._dilation_iterations)

        contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # length of contours and position of needed element to read is dependent on OpenCV version
        if len(contours) == 2:
            contours = contours[0]
        elif len(contours) == 3:
            contours = contours[1]
        else:
            print("Error")
            return None

        for contour in contours:
            if cv2.contourArea(contour) < self._minimal_area:
                continue

            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Motion detected"

        cv2.putText(frame, "Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)
        return frame

    @property
    def reference_frame(self):
        return self._reference_frame

    @reference_frame.setter
    def reference_frame(self, reference_frame):
        self._reference_frame = reference_frame
