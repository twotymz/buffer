import math
from os import listdir
from os.path import isfile, join
from PIL import Image, ImageStat
import pygame
import vpt


IMAGE_DIR = 'images'
CANVAS_RECT = pygame.Rect(0, 0, 1280, 1024)
ATTRACTION_CONSTANT = 0.1
DEFAULT_SPRING_LENGTH = 100


class Node(object):
    def __init__(self, path, image):
        self.path = path
        self.image = image
        self.median = ImageStat.Stat(image).median
        self.rect = pygame.Rect(0, 0, image.size[0], image.size[1])


class Vector(object):

    def __init__(self, magnitude=0, direction=0):
        self.direction = magnitude
        self.magnitude = direction


    @staticmethod
    def add(a, b):
        ax = a.magnitude * math.cos((math.pi / 180.0) * a.direction)
        ay = a.magnitude * math.sin((math.pi / 180.0) * a.direction)
        bx = b.magnitude * math.cos((math.pi / 180.0) * b.direction)
        by = b.magnitude * math.sin((math.pi / 180.0) * b.direction)

        ax += bx
        ay += by

        magnitude = math.sqrt(math.pow(ax, 2) + math.pow(ay, 2))
        direction = 0
        if magnitude != 0:
            direction = (180.0 / math.pi) * math.atan2(ay, ax)

        return Vector(magnitude, direction)


    def point(self):
        ax = self.magnitude * math.cos((math.pi / 180.0) * self.direction)
        ay = self.magnitude * math.sin((math.pi / 180.0) * self.direction)
        return (ax, ay)


def _color_difference(node_a, node_b):

    r = node_b.median[0] - node_a.median[0]
    g = node_b.median[1] - node_a.median[1]
    b = node_b.median[2] - node_a.median[2]

    return math.sqrt(r * r + g * g + b * b)


def _bearing_angle(start, end):

    start_x = start.rect.center[0]
    start_y = start.rect.center[1]
    end_x = end.rect.center[0]
    end_y = end.rect.center[1]

    half_x = start_x + ((end_x - start_x) / 2)
    half_y = start_y + ((end_y - start_y) / 2)

    diff_x = half_x - start_x
    diff_y = half_y - start_y

    if diff_x == 0:
        diff_x = 0.001

    if diff_y == 0:
        diff_y = 0.001

    angle = 0
    if abs(diff_x) > abs(diff_y):
        angle = math.tanh(diff_y / diff_x) * (180.0 / math.pi)
        if (diff_x < 0 and diff_y > 0) or (diff_x < 0 and diff_y < 0):
            angle += 180
    else:
        angle = math.tanh(diff_x / diff_y) * (180.0 / math.pi)
        if (diff_y < 0 and diff_x > 0) or (diff_y < 0 and diff_x < 0):
            angle += 180

    return angle


def _attraction_force(node_a, node_b):
    proximity = max(_color_difference(node_a, node_b), 1)
    force = ATTRACTION_CONSTANT * max(proximity - DEFAULT_SPRING_LENGTH, 0)
    angle = _bearing_angle(node_a, node_b)
    return Vector(force, angle)


def _position(input_image, similar_images):

    net_force = Vector(0, 0)

    for node in similar_images:
        net_force = Vector.add(net_force, _attraction_force(input_image, node[0]))

    print net_force.point()


def _main():

    input_images = []
    scene_images = []

    # Load input images in to "input_images".
    for filename in listdir(IMAGE_DIR):
        path = join(IMAGE_DIR, filename)
        if isfile(path):
            image = Image.open(path).convert('RGBA')
            input_images.append(Node(path, image))

    # Evaluate each input image against the images in the scene to figure
    # out the placement of the input image.
    while len(input_images) > 0:

        input_image = input_images.pop(0)

        '''
        if len(scene_images) == 0:
            # Place the first image in middle of the canvas.
            x_val = (CANVAS_RECT.width - input_image.image.size[0]) / 2
            y_val = (CANVAS_RECT.height - input_image.image.size[1]) / 2
            input_image.rect.center = (x_val, y_val)
            scene_images.append(input_image)
            continue
        '''

        tree = vpt.VP_tree(scene_images, _color_difference)
        results = []
        for similar_image in tree.find(input_image):
            results.append(similar_image)
            if len(results) == 3:
                break

        _position(input_image, results)
        scene_images.append(input_image)


if __name__ == '__main__':
    _main()
