
import logging
import math
from os import listdir
from os.path import isfile, join
import PIL
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance, ImageStat
import pygame
import time


BACKGROUND = (20, 20, 20)
DISPLAY_HEIGHT = 480
DISPLAY_WIDTH = 640
CANVAS_HEIGHT = 1024
CANVAS_WIDTH = 1280
STATE_GET_FRAME = 0
STATE_TRANSITION = 1
TRANSITION_TIME = 3.0
FLAG_CONTRAST = 1 << 0
FLAG_SATURATION = 1 << 1
IMAGE_DIR = 'images'


_canvas = None
_current_frame = None
_flags = 0
_frames = []
_input_images = []
_last_transition_time = 0
_previous_frame = None
_scene_pics = []
_transition_state = STATE_GET_FRAME
_transition_time = None


class Picture(object):
    def __init__(self, path, image):
        self.path = path
        self.image = image
        self.left_color = None
        self.right_color = None
        self.top_color = None
        self.bottom_color = None
        self.x = None
        self.y = None
        self.height = None
        self.width = None


def _get_avg_color(im, x, y, w, h):
    crop = im.crop((x, y, x+w, y+h))
    return ImageStat.Stat(crop).mean


def _test_rect(rect):

    global _scene_pics

    smallest_area = 999999

    for sp in _scene_pics:
        spr = pygame.Rect(sp.x, sp.y, sp.width, sp.height)

        logging.info('testing against {}, {}'.format(sp.path, str(spr)))
        logging.info('=' * 40)

        if rect.colliderect(spr):
            intersection = rect.clip(spr)
            area = (intersection.right - intersection.left) * (intersection.bottom - intersection.top)
            if area < smallest_area:
                smallest_area = area
        else:
            return False, None

    return True, smallest_area


def _position_image(pic):
    global _scene_pics, _canvas

    if len(_scene_pics) == 0:

        x_val = (_canvas.size[0] - pic.width) / 2
        y_val = (_canvas.size[1] - pic.height) / 2
        return x_val, y_val

    else:

        smallest_area = 999999
        winning_rect = None
        canvas_rect = pygame.Rect(0, 0, _canvas.size[0], _canvas.size[1])

        for sp in _scene_pics:

            logging.info('current pic {}'.format(sp.path))

            # Test the top...
            r = pygame.Rect(sp.x, sp.y - pic.height, pic.width, pic.height)
            r.clamp_ip(canvas_rect)
            logging.info('test top {}'.format(str(r)))

            collision, area = _test_rect(r)
            if not collision:
                return r.x, r.y
            else:
                if area < smallest_area:
                    smallest_area = area
                    winning_rect = r

            # Test the left...
            r = pygame.Rect(sp.x - pic.width, sp.y, pic.width, pic.height)
            r.clamp_ip(canvas_rect)
            logging.info('test left {}'.format(str(r)))

            collision, area = _test_rect(r)
            if not collision:
                return r.x, r.y
            else:
                if area < smallest_area:
                    smallest_area = area
                    winning_rect = r

            # Test the right...
            r = pygame.Rect(sp.x + sp.width, sp.y, pic.width, pic.height)
            r.clamp_ip(canvas_rect)
            logging.info('test right {}'.format(str(r)))

            collision, area = _test_rect(r)
            if not collision:
                return r.x, r.y
            else:
                if area < smallest_area:
                    smallest_area = area
                    winning_rect = r

            # Test the bottom...
            r = pygame.Rect(sp.x, sp.y + sp.height, pic.width, pic.height)
            r.clamp_ip(canvas_rect)
            logging.info('test bottom'.format(str(r)))

            collision, area = _test_rect(r)
            if not collision:
                return r.x, r.y
            else:
                if area < smallest_area:
                    smallest_area = area
                    winning_rect = r

        return winning_rect.x, winning_rect.y

    return 0, 0


def _load_image():

    global _input_images
    global _scene_pics

    if len(_input_images) == 0:
        return

    logging.info('-' * 20)

    pic = _input_images.pop(0)
    image = pic.image

    # Apply contrast boost.
    if _flags & FLAG_CONTRAST:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

    # Apply saturation boost.
    if _flags & FLAG_SATURATION:
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(2.0)

    #logging.info('loading image %s', pic.path)

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
        #logging.info('resizing image to %dx%d', new_width, new_height)
        image.thumbnail((new_width, new_height), PIL.Image.ANTIALIAS)

    pic.width = image.size[0]
    pic.height = image.size[1]

    #pic.left_color = _get_avg_color(image, 0, 0, image.size[0] / 2, image.size[1])
    #pic.right_color = _get_avg_color(image, image.size[0] / 2, 0, image.size[0] / 2, image.size[1])
    #pic.top_color = _get_avg_color(image, 0, 0, image.size[0], image.size[1] / 2)
    #pic.bottom_color = _get_avg_color(image, 0, image.size[1] / 2, image.size[0],  image.size[1] / 2)

    '''
    logging.info(
        'left {:.0f}, {:.0f}, {:.0f}'.format(pic.left_color[0], pic.left_color[1], pic.left_color[2])
    )
    logging.info(
        'right {:.0f}, {:.0f}, {:.0f}'.format(pic.right_color[0], pic.right_color[1], pic.right_color[2])
    )
    logging.info(
        'top {:.0f}, {:.0f}, {:.0f}'.format(pic.top_color[0], pic.top_color[1], pic.top_color[2])
    )
    logging.info(
        'bottom {:.0f}, {:.0f}, {:.0f}'.format(pic.bottom_color[0], pic.bottom_color[1], pic.bottom_color[2])
    )
    '''

    pic.x, pic.y = _position_image(pic)
    logging.info('final position %d, %d', pic.x, pic.y)

    # x_val, y_val is the upper left hand corner of the image.
    #x_val = (_canvas.size[0] - image.size[0]) / 2
    #y_val = (_canvas.size[1] - image.size[1]) / 2
    # place x_val and y_val in to the center of the new image.
    #pic.xy[0] = x_val + image.size[0] / 2
    #pic.xy[1] = y_val + image.size[1] / 2

    image.putalpha(255)
    #_canvas.paste(image, (pic.x, pic.y), image)

    d = ImageDraw.Draw(_canvas)
    d.rectangle([pic.x-1, pic.y-1, pic.x + pic.width - 2, pic.y + pic.height - 2], fill=(255,0,0,255), outline=(0,0,0,255))

    _generate_frame()
    _scene_pics .append(pic)


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

    foreground = _canvas.copy()

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
                #logging.info('new state %d', _transition_state)
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
            #logging.info('new state %d', _transition_state)
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
    global _input_images

    # Load input images in to "input_images".
    for f in listdir(IMAGE_DIR):
        path = join(IMAGE_DIR, f)
        if isfile(path):
            image = Image.open(path).convert('RGBA')
            _input_images.append(Picture(path, image))
            #logging.info('added {}'.format(path))

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
                if event.key == pygame.K_SPACE:
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
