import numpy as np
from PIL import ImageGrab, Image
import cv2
import time
from multiprocessing import Process
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class ScreenArea:
    def __init__(self, x, y, off_x, off_y):
        self.x = x
        self.y = y
        self.off_x = off_x
        self.off_y = off_y
        self.bbox = (self.x, self.y, self.x + self.off_x, self.y + self.off_y)


def ocr_puzzle(img):
    raw_img = pytesseract.image_to_string(img, config="--psm 12 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEF")
    try:
        split = raw_img[:-2].split('\n\n')
        puzzle_input = [split[(5 * i):(5 * i + 5)] for i in range(0, 5)]
        return puzzle_input
    except:
        raise RuntimeError("Failed to parse puzzle")


def ocr_answer(img):
    raw_img = pytesseract.image_to_string(img, config="--psm 12 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEF")
    try:
        raw_img.replace(" ", "")
        raw_img.replace("\n", "")
        raw_img.replace("\r\n", "")
        return raw_img
        # split = raw_img[:-2].split('\n\n')
        # puzzle_input = [split[(5 * i):(5 * i + 5)] for i in range(0, 5)]
        # return puzzle_input
    except:
        raise RuntimeError("Failed to parse answer")


def process_image(img):
    R, G, B = img.convert("RGB").split()
    r = R.load()
    g = G.load()
    b = B.load()
    w, h = img.size
    threshold = 170
    for i in range(w):
        for j in range(h):
            if g[i, j] < threshold:
                r[i, j] = 255
            else:
                r[i, j] = 0
            # r[i, j] = 255 - r[i, j]
    img = Image.merge("RGB", (R, R, R))
    return img


def process_puzzle(puzzle):
    img = general_process(puzzle)
    # cv2.imshow("window", img)
    puzzle_input = ocr_puzzle(img)
    return puzzle_input


def parse_answer(s):
    chars = list(s)
    built_str = ""
    arr = []
    counter = 0
    for c in chars:
        if counter == 2:
            counter = 0
            arr.append(built_str)
            built_str = ""
        built_str += c
        counter += 1
    if len(built_str) == 2:
        arr.append(built_str)
    return arr


def process_answer():
    img_1 = general_process(ScreenArea(830, 330, 150, 50))
    img_2 = general_process(ScreenArea(830, 400, 150, 50))
    img_3 = general_process(ScreenArea(830, 480, 150, 50))
    answers = []
    a1 = ocr_answer(img_1)
    a2 = ocr_answer(img_2)
    a3 = ocr_answer(img_3)
    answers.append("".join(ocr_answer(img_1).split()))
    if len(a2) > 0:
        answers.append("".join(ocr_answer(img_2).split()))
    if len(a3) > 0:
        answers.append("".join(ocr_answer(img_3).split()))
    final = answers[len(answers) - 1]
    parsed = parse_answer(final)
    return parsed


def general_process(area):
    img = ImageGrab.grab(bbox=area.bbox)
    img = process_image(img)
    img = np.array(img)
    return img


def main():
    process = Process()
    while True:
        puzzle = ScreenArea(320, 340, 380, 335)
        answer = ScreenArea(830, 330, 175, 200)
        puzzle_input = process_puzzle(puzzle)
        answer_input = process_answer()
        for row in puzzle_input:
            print(row)
        for n in answer_input:
            print(n)
        break
        time.sleep(0.025)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


main()
