import cv2
import time
import threading
import cv2
import time


class VideoCaptureAsync:
    def __init__(self, src=0, width=640, height=480):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            print('[!] Asynchroneous video capturing has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()


def test(n_frames=500, width=1280, height=720, async_flag=False):
    if async_flag:
        cap = VideoCaptureAsync(0)
    else:
        cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if async_flag:
        cap.start()
    t0 = time.time()
    i = 0
    while i < n_frames:
        _, frame = cap.read()
        cv2.imshow('Frame', frame)
        cv2.waitKey(1) & 0xFF
        i += 1
    print('[i] Frames per second: {:.2f}, async={}'.format(
        n_frames / (time.time() - t0), async_flag))
    if async_flag:
        cap.stop()
    cv2.destroyAllWindows()


def test(n_frames=500, width=1280, height=720, async_flag=False):
    if async_flag:
        # <----Change src to ip camera
        cap = VideoCaptureAsync(src=0, width=width, height=height)
        # <----Change src to ip camera 2
        cap1 = VideoCaptureAsync(src=1, width=width, height=height)
    else:
        cap = cv2.VideoCapture(0)
    if async_flag:
        cap.start()
        cap1.start()
    t0 = time.time()
    i = 0
    while i < n_frames:
        _, frame = cap.read()
        _, frame1 = cap1.read()
        cv2.imshow('Frame', frame)
        cv2.imshow('Frame 1', frame1)
        cv2.waitKey(1) & 0xFF
        i += 1
    print('[i] Frames per second: {:.2f}, async={}'.format(
        n_frames / (time.time() - t0), async_flag))
    if async_flag:
        cap.stop()
        cap1.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # test(n_frames=500, width=1280, height=720, async_flag=False)
    test(n_frames=500, width=1280, height=720, async_flag=True)
