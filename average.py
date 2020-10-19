
import PIL
from PIL import Image, ImageEnhance
import os
import os.path
from timeit import default_timer as timer

IMAGE_DIR = r'./images2'
CANVAS_HEIGHT = 960
CANVAS_WIDTH = 1280

max_red = [0] * CANVAS_WIDTH * CANVAS_HEIGHT
max_green = [0] * CANVAS_WIDTH * CANVAS_HEIGHT
max_blue = [0] * CANVAS_WIDTH * CANVAS_HEIGHT
max_counts = [0] * CANVAS_WIDTH * CANVAS_HEIGHT


def _load_image(canvas, image_path):

    global max_red, max_green, max_blue, max_counts

    try:
        image = Image.open(image_path).convert('RGBA')
    except:
        print('failed opening %s', _images[image_idx])
        return

    image = ImageEnhance.Contrast(image).enhance(2.0)
    image = ImageEnhance.Color(image).enhance(2.0)

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

    x1 = int((canvas.size[0] - image.size[0]) / 2)
    y1 = int((canvas.size[1] - image.size[1]) / 2)

    im_pixels = image.load()
    canvas_pixels = canvas.load()

    for y in range(image.size[1]):
        for x in range(image.size[0]):
            canvas_idx = canvas.size[0] * (y + y1) + (x + x1)
            max_counts[canvas_idx] += 1
            max_red[canvas_idx] = max(im_pixels[x,y][0], max_red[canvas_idx])
            max_green[canvas_idx] = max(im_pixels[x,y][1], max_green[canvas_idx])
            max_blue[canvas_idx] = max(im_pixels[x,y][2], max_blue[canvas_idx])

            #max_red[canvas_idx] = min(int((im_pixels[x, y][0] + max_red[canvas_idx]) / max_counts[canvas_idx]), 255)
            #max_green[canvas_idx] = min(int((im_pixels[x, y][1] + max_green[canvas_idx]) / max_counts[canvas_idx]), 255)
            #max_blue[canvas_idx] = min(int((im_pixels[x, y][2] + max_blue[canvas_idx]) / max_counts[canvas_idx]), 255)

    for canvas_idx in range(canvas.size[0] * canvas.size[1]):
        if max_counts[canvas_idx] > 0:
            y = int(canvas_idx / canvas.size[0])
            x = canvas_idx - canvas.size[0] * y
            canvas_pixels[x,y] = (
                min(int((canvas_pixels[x, y][0] + max_red[canvas_idx]) / 2), 255),             # Current pixel value plus max divided by alpha amount
                min(int((canvas_pixels[x, y][1] + max_green[canvas_idx]) / 2), 255),
                min(int((canvas_pixels[x, y][2] + max_blue[canvas_idx]) / 2), 255),
                255
            )

    print('Image {}'.format(image_path))

    print('Image R,G,B: {}, {}, {}'.format(
        im_pixels[image.size[0]/2, image.size[1]/2][0],
        im_pixels[image.size[0]/2, image.size[1]/2][1],
        im_pixels[image.size[0]/2, image.size[1]/2][2]
    ))

    print('Canvas R,G,B: {}, {}, {}'.format(
        canvas_pixels[CANVAS_WIDTH/2, CANVAS_HEIGHT/2][0],
        canvas_pixels[CANVAS_WIDTH/2, CANVAS_HEIGHT/2][1],
        canvas_pixels[CANVAS_WIDTH/2, CANVAS_HEIGHT/2][2]
    ))

    idx = CANVAS_WIDTH * int((CANVAS_HEIGHT / 2)) + int((CANVAS_WIDTH / 2))

    print('Max R, G, B, C: {}, {}, {}, {}'.format(
        max_red[idx],
        max_green[idx],
        max_blue[idx],
        max_counts[idx]
    ))


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

    print('Shallowest coverage is {}'.format(min(max_counts)))
    print('Deepest coverage is {}'.format(max(max_counts)))
    print('Average coverage is {}'.format(sum(max_counts) / len(max_counts)))

    canvas_pixels = canvas.load()
