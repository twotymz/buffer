
import PIL
from PIL import Image, ImageEnhance
import os
import os.path
from timeit import default_timer as timer


def _load_image(image_path):

    try:
        image = Image.open(image_path).convert('RGBA')
    except:
        print('failed opening %s', _images[image_idx])
        return

    return image

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

            red = min(int(red / (count + 1)), 255)
            green = min(int(green / (count + 1)), 255)
            blue = min(int(blue / (count + 1)), 255)

            canvas_pixels[x+x_val, y+y_val] = (
                red,
                green,
                blue,
                64
            )


if __name__ == '__main__':

    image = _load_image(r'.\images3\10.png')
    #image = _load_image(r'.\images2\51QnhsxyyEL._SY445_.jpg')

    pixels = image.load()

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if 484 <= x <= 794 and 289 <= y <= 733:
                print(x, y, pixels[x,y])
    #image.show()
