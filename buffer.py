
import logging
import math
import PIL
from PIL import Image, ImageFilter, ImageChops, ImageEnhance
import pygame


BACKGROUND = (20, 20, 20)
DISPLAY_HEIGHT = 1024
DISPLAY_WIDTH = 1280
CANVAS_HEIGHT = 640
CANVAS_WIDTH = 480


_images = [
    r'images/0.jpeg',
    r'images/1.jpg',
    r'images/2.jpg',
    r'images/3.jpg'
]

_output_surface = None


def _sobel(img):
    #if img.mode != "RGB":
    #    img = img.convert("RGB")
    out_image = Image.new(img.mode, img.size, None)
    imgdata = img.load()
    outdata = out_image.load()

    gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    gy = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

    for row in xrange(1, img.size[0]-1):
        for col in xrange(1, img.size[1]-1):
            pixel_gx = pixel_gy = 0
            #pxval = sum(imgdata[row, col])/3
            for i in range(-1, 2):
                for j in range(-1, 2):
                    val = sum(imgdata[row+i, col+j])/3
                    pixel_gx += gx[i+1][j+1] * val
                    pixel_gy += gy[i+1][j+1] * val
            newpixel = math.hypot(pixel_gx, pixel_gy)
            newpixel = 255 - int(newpixel)
            #newpixel = int(newpixel)
            outdata[row, col] = (newpixel, newpixel, newpixel)
    return out_image


def _load_image(slot):
    """ Load the image in the specified slot, process it, and update the
    output surface.
    """
    logging.info('loading image %s', _images[slot])

    try:
        image = Image.open(_images[slot])
    except:
        logging.error('failed opening %s', _images[slot])
        return

    # Resize the image if need be.
    new_width = None
    new_height = None

    if image.size[0] >= _output_surface.get_width():
        new_width = _output_surface.get_width() - 10

    if image.size[1] >= _output_surface.get_height():
        new_height = _output_surface.get_height() - 10

    if new_height or new_width:
        if not new_width:
            new_width = image.size[0]
        if not new_height:
            new_height = image.size[1]
        logging.info('resizing image to %dx%d', new_width, new_height)
        image.thumbnail((new_width, new_height), PIL.Image.ANTIALIAS)

    # Apply contrast boost.
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # Apply saturation boost.
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(1.5)

    image.putalpha(150)

    size = image.size
    mode = image.mode
    data = image.tobytes()
    image = pygame.image.fromstring(data, size, mode)

    x = (_output_surface.get_width() - size[0]) / 2
    y = (_output_surface.get_height() - size[1]) / 2
    #_output_surface.fill((BACKGROUND))
    _output_surface.blit(image, (x, y))


def _on_frame(screen):
    """ Update the screen. """
    global _output_surface
    #screen.blit(_output_surface, (0, 0))
    screen = pygame.display.get_surface()
    pygame.transform.scale(_output_surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT), screen)


def _main():

    global _output_surface

    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption('bufer v0')
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), 0)
    screen.fill(BACKGROUND)

    _output_surface = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
    _output_surface.fill((BACKGROUND))

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

        # Update the display.
        _on_frame(screen)

        pygame.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    _main()
