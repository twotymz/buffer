
import PIL
from PIL import Image, ImageEnhance, ImageStat
import os
import os.path
import random
import math
from timeit import default_timer as timer

IMAGE_DIR = r'./images2'
CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480
ACCUM_ALPHA = 64

objects = []
accum_reds = [0] * CANVAS_HEIGHT * CANVAS_WIDTH
accum_greens = [0] * CANVAS_HEIGHT * CANVAS_WIDTH
accum_blues = [0] * CANVAS_HEIGHT * CANVAS_WIDTH
accum_counts = [0] * CANVAS_HEIGHT * CANVAS_WIDTH

def _color_moments(image):

    s = ImageStat.Stat(image)

    red_accum = 0
    green_accum = 0
    blue_accum = 0

    im_pixels = image.load()

    npixels = image.size[0] * image.size[1]

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            red_accum += (im_pixels[x,y][0] - s.mean[0]) ** 3
            green_accum += (im_pixels[x,y][1] - s.mean[1]) ** 3
            blue_accum += (im_pixels[x,y][2] - s.mean[2]) ** 3

    skewness = [
        (red_accum / npixels) ** (1. / 3),
        (green_accum / npixels) ** (1. / 3),
        (blue_accum / npixels) ** (1. / 3)
    ]

    return [s.mean, s.stddev, skewness]


def _score(moments_1, moments_2, weights):
    score = 0
    for channel in range(3):        # R, G, B
        score += weights[0][channel] * abs((moments_1[0][channel] - moments_2[0][channel]))
        score += weights[1][channel] * abs((moments_1[1][channel] - moments_2[1][channel]))
        score += weights[2][channel] * abs((moments_1[2][channel] - moments_2[2][channel]))
    return score


def _place_image(canvas, image):
    """
    Returns the x and y co-ordinate the "image" should be placed at on the
    "canvas".
    """
    global objects

    moments = _color_moments(image)

    if len(objects) == 0:
        x_val = int((canvas.size[0] - image.size[0]) / 2)
        y_val = int((canvas.size[1] - image.size[1]) / 2)
    else:

        highest_score = 0
        winning_obj = None

        for o in objects:
            score = _score(moments, o['m'], [[1, 1, 1], [1, 1, 1], [1, 1, 1]])
            if score > highest_score:
                winning_obj = o
                highest_score = score

        # Choose a random side of the winning object to place the new image.
        side = random.randint(0, 4)
        if side == 0:   # top
            x_val = winning_obj['x']
            y_val = winning_obj['y'] + image.size[1]
        elif side == 1: # right
            x_val = winning_obj['x'] + winning_obj['w']
            y_val = winning_obj['y']
        elif side == 2: # bottom
            x_val = winning_obj['x']
            y_val = winning_obj['y'] + winning_obj['h']
        else:           # left
            x_val = winning_obj['x'] - image.size[0]
            y_val = winning_obj['y']

        if x_val < 0:
            x_val = 0
        if x_val + image.size[0] > canvas.size[0]:
            x_val = canvas.size[0] - image.size[0] - x_val
        if y_val < 0:
            y_val = 0
        if y_val + image.size[1] > canvas.size[1]:
            y_val = canvas.size[1] - image.size[1] - y_val

    objects.append({
        'i' : image,
        'x' : x_val,
        'y' : y_val,
        'w' : image.size[0],
        'h' : image.size[1],
        'm' : moments
    })

    return x_val, y_val


def _load_image(canvas, image_path):
    """
    Loads the image at "image_path" and places it on to the "canvas".
    """
    global accum_reds, accum_greens, accum_blues, accum_counts

    # Load the image.
    try:
        image = Image.open(image_path).convert('RGBA')
    except:
        print('failed opening %s', _images[image_idx])
        return

    # Apply contrast and saturation boost.
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(2.0)

    # Resize the image if need be.
    new_width = None
    new_height = None

    if image.size[0] >= canvas.size[0]:
        new_width = canvas.size[0] - 40

    if image.size[1] >= canvas.size[1]:
        new_height = canvas.size[1] - 40

    if new_height or new_width:
        if not new_width:
            new_width = image.size[0]
        if not new_height:
            new_height = image.size[1]
        image.thumbnail((new_width, new_height), PIL.Image.ANTIALIAS)

    # Figure out where the image should be placed within the canvas.
    x_val, y_val = _place_image(canvas, image)

    # Blend the image into the canvas.
    im_pixels = image.load()
    canvas_pixels = canvas.load()

    for x in range(image.size[0]):
        for y in range(image.size[1]):

            idx = canvas.size[0] * (y + y_val) + (x + x_val)

            count = accum_counts[idx] = accum_counts[idx] + 1
            red = accum_reds[idx] = accum_reds[idx] + im_pixels[x, y][0]
            green = accum_greens[idx] = accum_greens[idx] + im_pixels[x, y][1]
            blue = accum_blues[idx] = accum_blues[idx] + im_pixels[x, y][2]

            red = min(int(red / count), 255)
            green = min(int(green / count), 255)
            blue = min(int(blue / count), 255)

            canvas_pixels[x+x_val, y+y_val] = (
                red,
                green,
                blue,
                ACCUM_ALPHA
            )


if __name__ == '__main__':

    background_color = (0, 0, 0, 255)
    canvas = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT), background_color)

    total_secs = 0
    total_calls = 0

    for filename in os.listdir(IMAGE_DIR):
        start = timer()
        _load_image(canvas, os.path.join(IMAGE_DIR, filename))
        end = timer()
        total_secs += end - start
        total_calls += 1

    canvas.show()

    print('Avg time in _load_image() is {}'.format(
        total_secs / total_calls
    ))

    print('Shallowest coverage is {}'.format(min(accum_counts)))
    print('Deepest coverage is {}'.format(max(accum_counts)))
    print('Average coverage is {}'.format(sum(accum_counts) / len(accum_counts)))
