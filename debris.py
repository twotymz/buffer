
import PIL
from PIL import Image, ImageEnhance
import os
import os.path
from timeit import default_timer as timer

IMAGE_DIR = r'./images2'
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 960

accum_reds = [0] * CANVAS_HEIGHT * CANVAS_WIDTH
accum_greens = [0] * CANVAS_HEIGHT * CANVAS_WIDTH
accum_blues = [0] * CANVAS_HEIGHT * CANVAS_WIDTH
accum_counts = [0] * CANVAS_HEIGHT * CANVAS_WIDTH


def _load_image(canvas, image_path):

    global accum_reds, accum_greens, accum_blues, accum_counts

    try:
        image = Image.open(image_path).convert('RGBA')
    except:
        print('failed opening %s', _images[image_idx])
        return

    #image = ImageEnhance.Contrast(image).enhance(2)
    #image = ImageEnhance.Color(image).enhance(2)

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

    x_val = int((canvas.size[0] - image.size[0]) / 2)
    y_val = int((canvas.size[1] - image.size[1]) / 2)

    width, height = image.size

    im_pixels = image.load()
    canvas_pixels = canvas.load()

    for x in range(width):
        for y in range(height):

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
                255
            )


if __name__ == '__main__':

    background_color = (0, 0, 0, 255)
    canvas = Image.new('RGBA', (CANVAS_WIDTH, CANVAS_HEIGHT), background_color)

    _load_image(canvas, r'.\images2\51QnhsxyyEL._SY445_.jpg')
    canvas.save(r'.\images3\orig.png')
