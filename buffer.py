import logging
import math
import PIL
from PIL import Image, ImageEnhance, ImageStat
import pygame
import time
import random
import os
import os.path

IMAGE_DIR = r'.\images2'
BACKGROUND = (0, 0, 0)
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 960
STATE_GET_FRAME = 0
STATE_TRANSITION = 1
TRANSITION_TIME = 0.5
FLAG_CONTRAST = 1 << 0
FLAG_SATURATION = 1 << 1

_num_frames = 0
_images = []
_canvas = None
_current_frame = None
_flags = 0
_frames = []
_last_transition_time = 0
_previous_frame = None
_transition_state = STATE_GET_FRAME
_transition_time = None


_objects = []
_max_red = [0] * CANVAS_WIDTH * CANVAS_HEIGHT
_max_green = [0] * CANVAS_WIDTH * CANVAS_HEIGHT
_max_blue = [0] * CANVAS_WIDTH * CANVAS_HEIGHT
_max_counts = [0] * CANVAS_WIDTH * CANVAS_HEIGHT


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
    global _objects

    moments = _color_moments(image)

    if len(_objects) == 0:
        x_val = int((canvas.size[0] - image.size[0]) / 2)
        y_val = int((canvas.size[1] - image.size[1]) / 2)
    else:

        highest_score = 0
        winning_obj = None

        for o in _objects:
            score = _score(moments, o['m'], [[1, 1, 1], [1, 1, 1], [1, 1, 1]])
            if score > highest_score:
                winning_obj = o
                highest_score = score

        # Choose a random side of the winning object to place the new image.
        side = random.randint(0, 4)
        if side == 0:   # top
            logging.info('top')
            x_val = winning_obj['x']
            y_val = winning_obj['y'] - image.size[1]
        elif side == 1: # right
            logging.info('right')
            x_val = winning_obj['x'] + winning_obj['w']
            y_val = winning_obj['y']
        elif side == 2: # bottom
            logging.info('bottom')
            x_val = winning_obj['x']
            y_val = winning_obj['y'] + winning_obj['h']
        else:           # left
            logging.info('left')
            x_val = winning_obj['x'] - image.size[0]
            y_val = winning_obj['y']

        if x_val < 0:
            x_val = 0
        if x_val + image.size[0] > canvas.size[0]:
            x_val = canvas.size[0] - image.size[0]
        if y_val < 0:
            y_val = 0
        if y_val + image.size[1] > canvas.size[1]:
            y_val = canvas.size[1] - image.size[1]

    _objects.append({
        'i' : image,
        'x' : x_val,
        'y' : y_val,
        'w' : image.size[0],
        'h' : image.size[1],
        'm' : moments
    })

    return x_val, y_val


def _find_images():
    global _images
    for filename in os.listdir(IMAGE_DIR):
        name, ext = os.path.splitext(filename)
        if ext == '.jpg':
            _images.append(os.path.join(IMAGE_DIR, filename))


def _load_image():
    """ Load the image in the specified slot, process it, and update the
    output surface.
    """
    global _canvas, _num_frames, _flags
    global _max_red, _max_green, _max_blue, _max_counts

    image_idx = _num_frames % len(_images)
    logging.info('loading image %s', _images[image_idx])

    try:
        image = Image.open(_images[image_idx]).convert('RGBA')
    except:
        logging.error('failed opening %s', _images[image_idx])
        return

    # Resize the image if need be.
    new_width = None
    new_height = None

    if image.size[0] >= _canvas.size[0]:
        new_width = _canvas.size[0] - 40

    if image.size[1] >= _canvas.size[1]:
        new_height = _canvas.size[1] - 40

    if new_height or new_width:
        if not new_width:
            new_width = image.size[0]
        if not new_height:
            new_height = image.size[1]
        logging.info('resizing image to %dx%d', new_width, new_height)
        image.thumbnail((new_width, new_height), PIL.Image.ANTIALIAS)

    x1, y1 = _place_image(_canvas, image)

    im_pixels = image.load()
    canvas_pixels = _canvas.load()

    for y in range(image.size[1]):
        for x in range(image.size[0]):
            canvas_idx = _canvas.size[0] * (y + y1) + (x + x1)
            _max_counts[canvas_idx] += 1
            _max_red[canvas_idx] = min(int((im_pixels[x, y][0] + _max_red[canvas_idx]) / _max_counts[canvas_idx]), 255)
            _max_green[canvas_idx] = min(int((im_pixels[x, y][1] + _max_green[canvas_idx]) / _max_counts[canvas_idx]), 255)
            _max_blue[canvas_idx] = min(int((im_pixels[x, y][2] + _max_blue[canvas_idx]) / _max_counts[canvas_idx]), 255)

    for canvas_idx in range(_canvas.size[0] * _canvas.size[1]):
        if _max_counts[canvas_idx] > 0:
            y = int(canvas_idx / _canvas.size[0])
            x = canvas_idx - _canvas.size[0] * y
            canvas_pixels[x, y] = (
                min(int((canvas_pixels[x, y][0] + _max_red[canvas_idx]) / 2), 255),             # Current pixel value plus max divided by alpha amount
                min(int((canvas_pixels[x, y][1] + _max_green[canvas_idx]) / 2), 255),
                min(int((canvas_pixels[x, y][2] + _max_blue[canvas_idx]) / 2), 255),
                255
            )

    _generate_frame()


def _clear():

    global _canvas

    """ Clear the canvas. """
    background_color = (
        BACKGROUND[0],
        BACKGROUND[1],
        BACKGROUND[2],
        0
    )
    _canvas.paste(background_color, (0, 0, _canvas.size[0], _canvas.size[1]))
    _generate_frame()


def _generate_frame():
    """ Generate a new frame. """
    global _num_frames

    _num_frames += 1
    logging.info('num_frames = {}'.format(_num_frames))

    foreground = _canvas.copy()

    # Apply contrast boost.
    if _flags & FLAG_CONTRAST:
        enhancer = ImageEnhance.Contrast(foreground)
        foreground = enhancer.enhance(2.0)

    # Apply saturation boost.
    if _flags & FLAG_SATURATION:
        enhancer = ImageEnhance.Color(foreground)
        foreground = enhancer.enhance(2.0)

    background_color = (
        BACKGROUND[0],
        BACKGROUND[1],
        BACKGROUND[2],
        255
    )

    background = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT), background_color)
    background.paste(foreground, (0, 0), foreground)

    size = background.size
    mode = background.mode
    data = background.tobytes()
    image = pygame.image.fromstring(data, size, mode).convert()
    image = pygame.transform.scale(image, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
    _frames.append(image)


def _on_frame(screen):
    """ Update the screen. """

    global _current_frame
    global _last_transition_time
    global _previous_frame
    global _transition_state
    global _transition_time

    now = time.time()

    if _transition_state == STATE_GET_FRAME:
        if len(_frames) > 0:
            frame = _frames.pop()
            _previous_frame = _current_frame
            _current_frame = frame
            if _previous_frame:
                _transition_state = STATE_TRANSITION
                _last_transition_time = time.time()
                logging.info('new state %d', _transition_state)
        elif _current_frame:
            screen.fill(BACKGROUND)
            _current_frame.set_alpha(255)
            screen.blit(_current_frame, (0, 0))

    elif _transition_state == STATE_TRANSITION:

        _transition_time = now - _last_transition_time

        if _transition_time > TRANSITION_TIME:
            _transition_state = STATE_GET_FRAME
            screen.fill(BACKGROUND)
            _current_frame.set_alpha(255)
            screen.blit(_current_frame, (0, 0))
            logging.info('new state %d', _transition_state)
        else:
            prev_frame_alpha = 255 * (1.0 - (1.0 * _transition_time / TRANSITION_TIME))
            prev_frame_alpha = min(255, prev_frame_alpha)
            current_frame_alpha = 255 * (1.0 * _transition_time / TRANSITION_TIME)
            current_frame_alpha = min(255, current_frame_alpha)
            _previous_frame.set_alpha(prev_frame_alpha)
            _current_frame.set_alpha(current_frame_alpha)
            screen.blit(_previous_frame, (0, 0))
            screen.blit(_current_frame, (0, 0))


def _main():

    global _canvas
    global _flags

    _find_images()

    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption('buffer v0')
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), 0)
    screen.fill(BACKGROUND)

    background_color = (
        BACKGROUND[0],
        BACKGROUND[1],
        BACKGROUND[2],
        0
    )

    _canvas = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT), background_color)

    running = True
    while running:

        # Event handling.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    _load_image()
                elif event.key == pygame.K_c:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        _clear()
                    else:
                        _flags = _flags ^ FLAG_CONTRAST
                        logging.info('flags is %X', _flags)
                        _generate_frame()
                elif event.key == pygame.K_s:
                    _flags = _flags ^ FLAG_SATURATION
                    logging.info('flags is %X', _flags)
                    _generate_frame()

        # Update the display.
        _on_frame(screen)
        pygame.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    _main()
