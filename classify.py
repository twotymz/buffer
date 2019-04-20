import math
import PIL
from PIL import Image, ImageStat


def _color_moments(image_path):

    try:
        image = Image.open(image_path).convert('RGBA')
    except:
        print('failed opening %s', _images[image_idx])
        exit(0)

    s = ImageStat.Stat(image)

    red_accum = 0
    green_accum = 0
    blue_accum = 0

    im_pixels = image.load()

    npixels = image.size[0] * image.size[1]

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            red_accum += math.pow((im_pixels[x,y][0] - s.mean[0]), 3)
            green_accum += math.pow((im_pixels[x,y][1] - s.mean[1]), 3)
            blue_accum += math.pow((im_pixels[x,y][2] - s.mean[2]), 3)

    skewness = [
        math.pow(red_accum / npixels, 1/3),
        math.pow(green_accum / npixels, 1/3),
        math.pow(blue_accum / npixels, 1/3),
    ]

    return [s.mean, s.stddev, skewness]


def _score(moments_1, moments_2, weights):
    score = 0
    for channel in range(3):        # R, G, B
        score += weights[0][channel] * abs((moments_1[0][channel] - moments_2[0][channel]))
        score += weights[1][channel] * abs((moments_1[1][channel] - moments_2[1][channel]))
        score += weights[2][channel] * abs((moments_1[2][channel] - moments_2[2][channel]))
    return score


if __name__ == '__main__':

    #moments_1 = _color_moments(r'.\images2\da180a0059a7bad5e8175bf940f58f65.jpg')
    moments_1 = _color_moments(r'.\images2\cap021.jpg')
    moments_2 = _color_moments(r'.\images2\0kzy0vai0ei11.jpg')

    score = _score(moments_1, moments_2, [[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    print(score)
