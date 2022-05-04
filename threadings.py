import cv2
import argparse
from datetime import datetime
from threading import Thread
from datetime import datetime


class CountsPerSec:
    """
    Class that tracks the number of occurrences ("counts") of an
    arbitrary event and returns the frequency in occurrences
    (counts) per second. The caller must increment the count.
    """

    def __init__(self):
        self._start_time = None
        self._num_occurrences = 0

    def start(self):
        self._start_time = datetime.now()
        return self

    def increment(self):
        self._num_occurrences += 1

    def countsPerSec(self):
        elapsed_time = (datetime.now() - self._start_time).total_seconds()
        return self._num_occurrences / elapsed_time


def putIterationsPerSec(frame, iterations_per_sec):
    """
    Add iterations per second text to lower-left corner of a frame.
    """

    cv2.putText(frame, "{:.0f} iterations/sec".format(iterations_per_sec),
                (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255))
    return frame


class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture("German.MOV")
        # Define the codec and create VideoWriter object
        # Define the codec and create VideoWriter object
        width = 2 * int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
        height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
        size = (width, height)
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter('output.mp4', self.fourcc, 5, size)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def stop(self):
        self.stopped = True


class VideoShow:
    """
    Class that continuously shows a frame using a dedicated thread.
    """

    def __init__(self, frame=None):
        self.frame = frame
        self.stopped = False

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        while not self.stopped:
            # cv2.namedWindow("preview", cv2.WINDOW_NORMAL)
            cv2.imshow("Video", self.frame)
            if cv2.waitKey(1) % 256 == 27:
                self.stopped = True

    def stop(self):
        self.stopped = True
