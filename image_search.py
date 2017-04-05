import math
from os import listdir
from os.path import isfile, join
from PIL import Image, ImageStat
import vpt


IMAGE_DIR = 'images'


class Picture(object):
    def __init__(self, path, image):
        self.path = path
        self.image = image
        self.median = ImageStat.Stat(image).median


def color_difference(a, b):

    r = b.median[0] - a.median[0]
    g = b.median[1] - a.median[1]
    b = b.median[2] - b.median[2]

    return math.sqrt(r * r + g * g + b * b)


if __name__ == '__main__':

    input_images = []
    scene_images = []

    # Load input images in to "input_images".
    for f in listdir(IMAGE_DIR):
        path = join(IMAGE_DIR, f)
        if isfile(path):
            image = Image.open(path).convert('RGBA')
            input_images.append(Picture(path, image))

    # Evaluate each input image against the images in the scene to figure
    # out the placement of the input image.
    while len(input_images) > 0:

        input_image = input_images.pop(0)

        if len(scene_images) == 0:
            scene_images.append(input_image)
            continue

        tree = vpt.VP_tree(scene_images, color_difference)
        results = []
        for r in tree.find(input_image):
            results.append(r)
            if len(results) == 3:
                break

        scene_images.append(input_image)
