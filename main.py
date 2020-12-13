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


def solve_row(puzzle, row_index, used_pos, sequence, buffer):
    if len(sequence) > buffer:
        return None
    for i, col in enumerate(puzzle[row_index]):
        if i != used_pos:
            if col == sequence[0]:
                if len(sequence) == 1:
                    return [(i, row_index)]
                else:
                    rest = solve_column(puzzle, i, row_index, sequence[1:], buffer - 1)
                    if rest is not None:
                        return [(i, row_index)] + rest
            rest = solve_column(puzzle, i, row_index, sequence, buffer - 1)
            if rest is not None:
                return [(i, row_index)] + rest
    return None


def solve_column(puzzle, col_index, used_pos, sequence, buffer):
    if len(sequence) > buffer:
        return None
    for i in range(0, len(puzzle)):
        row = puzzle[i][col_index]
        if i != used_pos:
            if row == sequence[0]:
                if len(sequence) == 1:
                    return [(col_index, i)]
                else:
                    rest = solve_row(puzzle, i, col_index, sequence[1:], buffer - 1)
                    if rest is not None:
                        return [(col_index, i)] + rest
            rest = solve_row(puzzle, i, col_index, sequence, buffer - 1)
            if rest is not None:
                return [(col_index, i)] + rest
    return None


def solver(puzzle, answer):
    return solve_row(puzzle, 0, None, answer, 4)


def print_res(res):
    print(f"First move: {res[0]}")
    for i, step in enumerate(res):
        if i == 0:
            continue
        diff_x = res[i][0] - res[i - 1][0]
        diff_y = res[i][1] - res[i - 1][1]
        if diff_x != 0:
            direction = "right" if diff_x > 0 else "right"
            print(f"{direction} {diff_x}")
        else:
            direction = "down" if diff_y > 0 else "up"
            print(f"{direction} {diff_y}")


def main():
    process = Process()
    puzzle = ScreenArea(320, 340, 380, 335)
    answer = ScreenArea(830, 330, 175, 200)
    puzzle_input = process_puzzle(puzzle)
    answer_input = process_answer()
    for row in puzzle_input:
        print(row)
    for n in answer_input:
        print(n)
    #if answer is not picked up correctly a harccode is needed
    #answer_input = ["E9", "55"]
    res = solver(puzzle_input, answer_input)
    print_res(res)


main()
