
import logging
import math
import PIL
from PIL import Image, ImageFilter, ImageChops, ImageEnhance
import pygame
import time


BACKGROUND = (20, 20, 20)
DISPLAY_HEIGHT = 480
DISPLAY_WIDTH = 640
CANVAS_HEIGHT = 480
CANVAS_WIDTH = 640
STATE_GET_FRAME = 0
STATE_TRANSITION = 1
TRANSITION_TIME = 3.0
FLAG_CONTRAST = 1 << 0
FLAG_SATURATION = 1 << 1

_images = [
    r'images/0.jpeg',
    r'images/1.jpg',
    r'images/2.jpg',
    r'images/3.jpg'
]

_canvas = None
_current_frame = None
_flags = 0
_frames = []
_last_transition_time = 0
_previous_frame = None
_transition_state = STATE_GET_FRAME
_transition_time = None


def _load_image(slot):
    """ Load the image in the specified slot, process it, and update the
    output surface.
    """
    logging.info('loading image %s', _images[slot])

    try:
        image = Image.open(_images[slot]).convert('RGBA')
    except Exception, e:
        logging.error('failed opening %s (%s)', _images[slot], str(e))
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

    x_val = (_canvas.size[0] - image.size[0]) / 2
    y_val = (_canvas.size[1] - image.size[1]) / 2
    image.putalpha(150)
    _canvas.paste(image, (x_val, y_val), image)

    _generate_frame()


def _clear():
    """ Clear the canvas. """
    background_color = (
        BACKGROUND[0],
        BACKGROUND[1],
        BACKGROUND[2],
        0
    )
    _canvas.paste(background_color, None)
    _generate_frame()


def _generate_frame():
    """ Generate a new frame. """

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

    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption('bufer v0')
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
                    _load_image(0)
                elif event.key == pygame.K_2:
                    _load_image(1)
                elif event.key == pygame.K_3:
                    _load_image(2)
                elif event.key == pygame.K_4:
                    _load_image(3)
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
