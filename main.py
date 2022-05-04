
import cv2
import subprocess
from imutils import paths
import numpy as np
import imutils
import time
from threadings import CountsPerSec, putIterationsPerSec, VideoGet, VideoShow
import os

from passporteye import read_mrz
import tkinter as tk
import asyncio
from multiprocessing import Process, Queue

root = tk.Tk()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()


window_width = int(screen_width/3)
window_height = int(window_width / (screen_width / screen_height))

# DISPLAY MATRIX
# -------------------------------------
# |           |           |           |
# |     1     |     2     |     3     |
# |           |           |           |
# -------------------------------------
# |           |           |           |
# |     4     |     5     |     6     |
# |           |           |           |
# -------------------------------------
# |           |           |           |
# |     7     |     8     |     9     |
# |           |           |           |
# -------------------------------------

WIN_POS = {
    1: [0, 0],
    2: [window_width, 0],
    3: [window_width * 2, 0],
    4: [0, window_height],
    5: [window_width, window_height],
    6: [window_width * 2, window_height],
    7: [0, window_height * 2],
    8: [window_width, window_height * 2],
    9: [window_width * 2, window_height * 2],

}


def Display3x3(Name, Fr, Position):
    """Name is the name of your window, Fr is the desired Frame to display, Position is (1->9) check the Display Matrix"""

    WinName = str(Name)
    resized_window1 = cv2.resize(Fr, (window_width, window_height))

    try:
        POS = WIN_POS[Position]
    except:
        print("*** ERROR Enter a Position Value from 1 -> 9 only. Check Display Matrix ***")
        exit()
    cv2.namedWindow(WinName)
    cv2.moveWindow(WinName, POS[0], POS[1])
    cv2.imshow(WinName, resized_window1)


async def threadVideoGet(source=0):
    """
    Dedicated thread for grabbing video frames with VideoGet object.
    Main thread shows video frames.
    """
    video_getter = VideoGet(source).start()
    cps = CountsPerSec().start()

    while True:
        if (cv2.waitKey(1) % 256 == 27) or video_getter.stopped:
            video_getter.stop()
            return

        frame = video_getter.frame
        thresh_frame = frame
        frame = putIterationsPerSec(frame, cps.countsPerSec())
        gray, blackhat, gradX, thresh = await mrz(frame)

        # cv2.imshow("web", frame)
        Display3x3("image", frame, 1)
        if type(gray) != type(None):
            Display3x3("gray", gray, 2)
            Display3x3("blackhat", blackhat, 3)
            Display3x3("gradX", gradX, 4)
            Display3x3("thresh", thresh, 5)
            gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            blackhat = cv2.cvtColor(blackhat, cv2.COLOR_GRAY2RGB)
            gradX = cv2.cvtColor(gradX, cv2.COLOR_GRAY2RGB)
            thresh_frame = thresh

        final = cv2.hconcat([frame, thresh_frame])
        video_getter.out.write(final)
        cps.increment()


async def mrz(img):
    start_time = time.time()

    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
    sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
    # image = imutils.resize(img, height=600)
    image = img.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)

    gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradX = np.absolute(gradX)
    (minVal, maxVal) = (np.min(gradX), np.max(gradX))
    gradX = (255 * ((gradX - minVal) / (maxVal - minVal))).astype("uint8")

    gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
    thresh = cv2.threshold(
        gradX, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
    thresh = cv2.erode(thresh, None, iterations=4)

    p = int(image.shape[1] * 0.05)
    thresh[:, 0:p] = 0
    thresh[:, image.shape[1] - p:] = 0

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        crWidth = w / float(gray.shape[1])

        if ar >= 5 and crWidth >= 0.25:
            pX = int((x + w) * 0.03)
            pY = int((y + h) * 0.03)
            (x, y) = (x - pX, y - pY)
            (w, h) = (w + (pX * 2), h + (pY * 2))

            roi = image[y:y + h, x:x + w].copy()
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            thresh = np.expand_dims(thresh, axis=2)
            thresh_1 = np.concatenate([thresh, thresh], axis=2)
            thresh = np.concatenate([thresh_1, thresh], axis=2)
            img = np.concatenate([img, thresh], axis=0)
            return (gray, blackhat, gradX, thresh)

    return (None, None, None, None)
    # try:
    #     image_bytes = cv2.imencode('.jpg', roi)[1].tobytes()
    #     print("HOG time work:", str(time.time() - start_time)[:5])
    # except:
    #     print("Horizontal HOG algorithm found nothing!")
    #     return None
    # try:
    #     mrz_image = await Tesseract(image, image_bytes)
    #     return mrz_image
    # except:
    #     print("Tesseract found nothing!")
    #     return None


async def Tesseract(image, image_bytes):
    start_time = time.time()
    mrz = list(read_mrz(image_bytes).to_dict().values())[2]
    print(mrz)
    y0, dy = 150, 40
    for i, line in enumerate(mrz.split('\n')):
        y = y0 + i*dy
        cv2.putText(image, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2, cv2.LINE_AA)
    print("Tesseract time work:", str(time.time() - start_time)[:5])
    return image


if __name__ == '__main__':
    asyncio.run(threadVideoGet())
