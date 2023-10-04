from math import *
import numpy as np

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import cv2 as cv


def get_contours(image, blur=10, offsets=(0, 0), method='canny'):
    imgray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    if method == 'canny':
        bw = cv.blur(cv.Canny(imgray, 0, 255), (blur, blur))
    elif method == 'threshold':
        _, bw = cv.threshold(imgray, 127, 255, cv.THRESH_BINARY)
    else:
        assert False

    # cv.imshow('BW', bw)
    # cv.waitKey()

    contours, hierarchy = cv.findContours(bw, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

    cnt = []

    for c in contours:
        ls = c.tolist()
        tl = []

        for k in ls:
            tl.append([k[0][0] + offsets[0],
                       k[0][1] + offsets[1]])

        cnt.append(tl)

    return sorted(cnt, key = len, reverse=True)


def arc(x, y, r, a, d=0.1):
    a_rad = radians(a)
    t = np.arange(0, a_rad, d)
    res = np.c_[np.sin(t) * r + x, np.cos(t) * r + y]
    return res.tolist()


def text(string, x, y, s, font="arial.ttf"):
    img = Image.new('RGB', (s * len(string), s * 3 * (string.count('\n') + 1)))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font, s * 100 // 72)
    draw.text((0, -25 / 100 * s), string, (255, 255, 255), font=font)
    open_cv_image = np.array(img)
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    return get_contours(open_cv_image, 1, (x, y), 'threshold')
