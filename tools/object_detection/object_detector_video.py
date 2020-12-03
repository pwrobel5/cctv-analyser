import cv2
import numpy as np
import imutils
import time
import sys
import os
from.cfg import parameters_detection


class ObjectDetectorVideo:
    def __init__(self):
        self.input_video_path = None
        self.output_video_path = "samples/sample_new.avi"

        # the neural network configuration
        self.config_path = "cfg/yolov3.cfg"
        # the YOLO net weights file
        self.weights_path = "weights/yolov3.weights"
        # weights_path = "weights/yolov3-tiny.weights"

        # loading all the class labels (objects)
        self.labels = open("data/coco.names").read().strip().split("\n")
        # generating colors for each object for later plotting
        self.colors = np.random.randint(0, 255, size=(len(self.labels), 3), dtype="uint8")

        # load the YOLO network
        self.net = cv2.dnn.readNetFromDarknet(self.config_path, self.weights_path)
        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        self.vs = None
        self.writer = None
        self.W = None
        self.H = None
        self.prop = None
        self.total = None

    def upload_video(self, input_video_path):
        self.input_video_path = input_video_path
        # initialize the video stream, pointer to output video file, and
        # frame dimensions
        self.vs = cv2.VideoCapture(input_video_path)
        self.writer = None
        (self.W, self.H) = (None, None)

        # try to determine the total number of frames in the video file
        try:
            self.prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT if imutils.is_cv2() \
                else cv2.CAP_PROP_FRAME_COUNT
            self.total = int(self.vs.get(self.prop))
            print("[INFO] {} total frames in video".format(self.total))
        # an error occurred while trying to determine the total
        # number of frames in the video file
        except:
            print("[INFO] could not determine # of frames in video")
            print("[INFO] no approx. completion time can be provided")
            self.total = -1

    def detect_objects(self):
        if self.input_video_path == None:
            print("No video for object detection")
            return
        # loop over frames from the video file stream
        while True:
            # read the next frame from the file
            (grabbed, frame) = self.vs.read()
            # if the frame was not grabbed, then we have reached the end
            # of the stream
            if not grabbed:
                break
            # if the frame dimensions are empty, grab them
            if self.W is None or self.H is None:
                (self.H, self.W) = frame.shape[:2]

            # construct a blob from the input frame and then perform a forward
            # pass of the YOLO object detector, giving us our bounding boxes
            # and associated probabilities
            blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                                         swapRB=True, crop=False)
            self.net.setInput(blob)
            start = time.time()
            layerOutputs = self.net.forward(self.ln)
            end = time.time()
            # initialize our lists of detected bounding boxes, confidences,
            # and class IDs, respectively
            boxes = []
            confidences = []
            classIDs = []
            # loop over each of the layer outputs
            for output in layerOutputs:
                # loop over each of the detections
                for detection in output:
                    # extract the class ID and confidence (i.e., probability)
                    # of the current object detection
                    scores = detection[5:]
                    classID = np.argmax(scores)
                    confidence = scores[classID]
                    # filter out weak predictions by ensuring the detected
                    # probability is greater than the minimum probability
                    if confidence > parameters_detection.CONFIDENCE:
                        # scale the bounding box coordinates back relative to
                        # the size of the image, keeping in mind that YOLO
                        # actually returns the center (x, y)-coordinates of
                        # the bounding box followed by the boxes' width and
                        # height
                        box = detection[0:4] * np.array([self.W, self.H, self.W, self.H])
                        (centerX, centerY, width, height) = box.astype("int")
                        # use the center (x, y)-coordinates to derive the top
                        # and and left corner of the bounding box
                        x = int(centerX - (width / 2))
                        y = int(centerY - (height / 2))
                        # update our list of bounding box coordinates,
                        # confidences, and class IDs
                        boxes.append([x, y, int(width), int(height)])
                        confidences.append(float(confidence))
                        classIDs.append(classID)
            # apply non-maxima suppression to suppress weak, overlapping
            # bounding boxes
            idxs = cv2.dnn.NMSBoxes(boxes, confidences, parameters_detection.CONFIDENCE,
                                    parameters_detection.SCORE_THRESHOLD)  # TODO not sure which threshold to use
            # ensure at least one detection exists
            if len(idxs) > 0:
                # loop over the indexes we are keeping
                for i in idxs.flatten():
                    # extract the bounding box coordinates
                    (x, y) = (boxes[i][0], boxes[i][1])
                    (w, h) = (boxes[i][2], boxes[i][3])
                    # draw a bounding box rectangle and label on the frame
                    color = [int(c) for c in self.colors[classIDs[i]]]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    text = "{}: {:.4f}".format(self.labels[classIDs[i]],
                                               confidences[i])
                    cv2.putText(frame, text, (x, y - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            # check if the video writer is None
            if self.writer is None:
                # initialize our video writer
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                self.writer = cv2.VideoWriter(self.output_video_path, fourcc, 30,
                                         (frame.shape[1], frame.shape[0]), True)
                # some information on processing single frame
                if self.total > 0:
                    elap = (end - start)
                    print("[INFO] single frame took {:.4f} seconds".format(elap))
                    print("[INFO] estimated total time to finish: {:.4f}".format(
                        elap * self.total))
            # write the output frame to disk
            self.writer.write(frame)
        # release the file pointers
        print("[INFO] cleaning up...")
        self.writer.release()
        self.vs.release()