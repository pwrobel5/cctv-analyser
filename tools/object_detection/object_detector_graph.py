import cv2
import numpy as np
import time
from .cfg import parameters_detection
import threading


class ObjectDetectorGraph:
    def __init__(self, app):
        self.frames = None
        self.frame = None
        self.app = app

        # the neural network configuration
        self.config_path = "tools/object_detection/cfg/yolov3.cfg"
        # the YOLO net weights file
        self.weights_path = "tools/object_detection/weights/yolov3.weights"
        # weights_path = "weights/yolov3-tiny.weights"

        # loading all the class labels (objects)
        self.labels = open("tools/object_detection/data/coco.names").read().strip().split("\n")
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


        #CUDA = torch.cuda.is_available()

        self._lock = threading.Lock()

    def upload_frame(self, frame):
        self.frame = frame

    def upload_frames(self, frames):
        self.frames = frames

    def detect_objects(self, frames, index):

        with self._lock:
            found_objects = []
            #print(len(frames))
            self.upload_frames(frames)
            for frame in self.frames:
                self.frame = frame
                # if the frame dimensions are empty, grab them
                if self.W is None or self.H is None:
                    (self.H, self.W) = self.frame.shape[:2]

                # construct a blob from the input frame and then perform a forward
                # pass of the YOLO object detector, giving us our bounding boxes
                # and associated probabilities
                blob = cv2.dnn.blobFromImage(self.frame, 1 / 255.0, (416, 416),
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
                                        parameters_detection.SCORE_THRESHOLD)
                # ensure at least one detection exists
                if len(idxs) > 0:
                    # loop over the indexes we are keeping
                    for i in idxs.flatten():
                        # extract the bounding box coordinates
                        (x, y) = (boxes[i][0], boxes[i][1])
                        (w, h) = (boxes[i][2], boxes[i][3])
                        # draw a bounding box rectangle and label on the frame
                        color = [int(c) for c in self.colors[classIDs[i]]]
                        cv2.rectangle(self.frame, (x, y), (x + w, y + h), color, 2)
                        text = "{}: {:.4f}".format(self.labels[classIDs[i]],
                                                   confidences[i])
                        if not (self.labels[classIDs[i]] in found_objects):
                            found_objects.append(self.labels[classIDs[i]])
                        #print("IND: " + str(index))
                        #print(text)



                        cv2.putText(self.frame, text, (x, y - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                elap = (end - start)
                print("[INFO] single frame took {:.4f} seconds".format(elap))

            if len(frames) > 0:
                self._save(index, found_objects)
            #print("FINISHED " + str(index) )

    def _save(self, index, objects):
        f = open("annotations.txt", "a")
        f.write(self.app.get_moving_times(index)[0] + " - " + self.app.get_moving_times(index)[1] + ": ")
        for o in objects:
            f.write(o + " ")
        f.write(" \n")
        f.close()

