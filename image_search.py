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

    images = []
    scene_images = []

    for f in listdir(IMAGE_DIR):
        path = join(IMAGE_DIR, f)
        if isfile(path):
            image = Image.open(path).convert('RGBA')
            images.append(Picture(path, image))

    while len(images) > 0:

        input_image = images.pop(0)

        if len(scene_images) == 0:
            scene_images.append(input_image)
            continue

        tree = vpt.VP_tree(scene_images, color_difference)
        results = tree.find(input_image)

        print input_image.path
        n = 0
        for r in results:
            print '% 5d %s' % (r[1], r[0].path)
            n += 1
            if n >= 5:
                break
        print '-' * 20

        scene_images.append(input_image)
