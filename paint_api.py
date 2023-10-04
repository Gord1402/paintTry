import os
import sys
import time
from math import sqrt

import keyboard
import pyautogui
from PIL import Image


def color_distance(c1, c2):
    """
    This function gets distance between two colors.
    """
    return sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2)


# approximate color to palette
def approx(c, palette):
    """
    This function gets the most similarity between color and palette
    """
    minimum = 99999
    minimum_c = None

    for palette_color in palette.keys():
        dist = color_distance(palette_color, c)
        if minimum > dist:
            minimum = dist
            minimum_c = palette_color

    return minimum_c


class Paint:
    def __init__(self, paint_set=None):
        """
        Init paint tool.
        paint_set - Path to folder with app definition
        """
        if paint_set is None:
            paint_set = f'{filter(lambda s: s.find("site-packages") != -1, sys.path).__next__()}{os.sep}' \
                        f'PaintApi{os.sep}paint_set'
        self.paint_set = paint_set
        self.palette = None
        self.palette_colors = {}
        self.drawing_space = None
        self.tools = {}

    def connect(self):
        """
        Founding the paint window.
        """
        print('Finding a paint app.')
        try:
            self.palette = list(pyautogui.locateOnScreen(self.paint_set + '\\palette\\palette.png', confidence=0.9))[:2]
            start = list(pyautogui.locateOnScreen(self.paint_set + '\\draw_space\\start.png', confidence=0.9))
            self.drawing_space = [start[0] + 40, start[1] + start[3] + 40]
            with open(self.paint_set + '\\tools\\label.txt', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    name, file, align, offset_x, offset_y = line.replace('\n', '').split(' ')

                    offset_x = int(offset_x)
                    offset_y = int(offset_y)

                    pos = list(pyautogui.locateOnScreen(self.paint_set + f'\\tools\\{file}', confidence=0.9))
                    if align == 'center':
                        pos = [pos[0] + pos[2] // 2 + offset_x, pos[1] + pos[3] // 2 + offset_y]
                    elif align == 'topLeft':
                        pos = [pos[0] + offset_x, pos[1] + offset_y]
                    elif align == 'topRight':
                        pos = [pos[0] + pos[2] + offset_x, pos[1] + offset_y]
                    elif align == 'bottomLeft':
                        pos = [pos[0] + offset_x, pos[1] + pos[3] + offset_y]
                    elif align == 'bottomRight':
                        pos = [pos[0] + pos[2] + offset_x, pos[1] + pos[3] + offset_y]
                    else:
                        print(f'Align type "{align}" not found.')
                        return
                    self.tools[name] = pos
        except TypeError as e:
            print('Paint app not founded. Check paint_set.')
            return

        palette_image = Image.open(self.paint_set + '\\palette\\palette.png')
        w, h = palette_image.width, palette_image.height

        palette_mask_image = Image.open(self.paint_set + '\\palette\\palette_mask.png')

        for x in range(w):
            for y in range(h):
                if palette_mask_image.getpixel((x, y))[0] > 0:
                    self.palette_colors[palette_image.getpixel((x, y))] = (x, y)

        print("Paint app founded.\nDon't move app!")

    def set_color(self, color_rgb):
        """
        Sets color of the brush.
        """
        pal_col = approx(color_rgb, self.palette_colors)

        if pal_col is None:
            print('Check palette_mask color not founded.')
            return

        minimum_cord = self.palette_colors[pal_col]

        pyautogui.click(self.palette[0] + minimum_cord[0], self.palette[1] + minimum_cord[1], _pause=False)

    def set_tool(self, name):
        """
        Sets tools from paint_set/tools/label.txt
        """
        if keyboard.is_pressed('q'):
            return
        pyautogui.click(self.tools[name])

    def use_at(self, tool, x, y):
        """
        Uses tool at x, y
        """
        if keyboard.is_pressed('q'):
            return
        self.set_tool(tool)
        pyautogui.click(x + self.drawing_space[0], y + self.drawing_space[1])

    def approx_image(self, image):
        """
        Approximate image colors to palette
        """
        w, h = image.width, image.height
        ap_im = Image.new('RGB', (w, h))

        for x in range(w):
            for y in range(h):
                ap_im.putpixel((x, y), approx(image.getpixel((x, y)), self.palette_colors))

        return ap_im

    def draw_points(self, points, pause_time=0.05, _pause=False, loop=True):
        """
        Draws polygon.
        Long press q key to stop.
        """
        if keyboard.is_pressed('q'):
            return
        pyautogui.mouseDown(points[0][0] + self.drawing_space[0], points[0][1] + self.drawing_space[1],
                            _pause=_pause)
        time.sleep(pause_time)

        for point in points[1:]:
            if keyboard.is_pressed('q'):
                return
            pyautogui.moveTo(point[0] + self.drawing_space[0], point[1] + self.drawing_space[1],
                             duration=pause_time,
                             _pause=_pause)
            time.sleep(pause_time)
        if loop:
            pyautogui.moveTo(points[0][0] + self.drawing_space[0], points[0][1] + self.drawing_space[1],
                             duration=pause_time,
                             _pause=_pause)
            time.sleep(pause_time)
        pyautogui.mouseUp(_pause=_pause)
        time.sleep(pause_time)

    def multi_draw(self, contours, pause_time=0.05, _pause=False, loop=True):
        """
        Draws multiple polygons.
        Long press q key to stop.
        """
        for c in contours:
            if keyboard.is_pressed('q'):
                return
            self.draw_points(c, pause_time, _pause, loop)

    def draw_image(self, image, x, y, pause_time=0.05, brush_size=1):
        """
        Draws images by dots.
        Long press q key to stop.
        """
        if keyboard.is_pressed('q'):
            return
        w, h = image.width, image.height
        c = approx(image.getpixel((x, y)), self.palette_colors)
        self.set_color(c)
        pyautogui.mouseDown(x + self.drawing_space[0], y + self.drawing_space[1], _pause=False)
        time.sleep(pause_time)

        for xx in range(0, w, brush_size):
            for yy in range(0, h, brush_size):
                if keyboard.is_pressed('q'):
                    return
                if c != approx(image.getpixel((x + xx, y + yy)), self.palette_colors):
                    c = approx(image.getpixel((x + xx, y + yy)), self.palette_colors)
                    pyautogui.mouseUp(_pause=False)
                    time.sleep(pause_time)
                    self.set_color(c)
                    pyautogui.mouseDown(x + xx + self.drawing_space[0], y + yy + self.drawing_space[1], _pause=False)
                    time.sleep(pause_time)
                    pyautogui.moveTo(x + xx + self.drawing_space[0], y + yy + self.drawing_space[1] + brush_size - 1,
                                     _pause=False)
                    time.sleep(pause_time)
                pyautogui.moveTo(x + xx + self.drawing_space[0], y + yy + self.drawing_space[1], _pause=False)
                time.sleep(pause_time)
            pyautogui.mouseUp(_pause=False)
            time.sleep(pause_time if pause_time > 0 else 0.3)
