
import io
import requests
from PIL import Image

if __name__ == '__main__':
    url = 'https://unsplash.it/{}/{}?random'.format(320, 240)
    r = requests.get(url)

    print(r.status_code)
    print(r.content)

    if r.status_code == 200:
        bytes_io = io.BytesIO(r.content)
        image = Image.open(bytes_io)
        image.show()
