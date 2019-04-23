
from bs4 import BeautifulSoup
import requests
import json

class ImageSearch (object):

    def __init__(self):
        self._done = True
        self._page = 0
        self._search_term = None


    def set_search_term(self, term):
        """ Set the search term for the image search. """
        self._done = False
        self._page = 0
        self._search_term = term


    def is_done(self):
        """ Is the search done. """
        return self._done


    def run(self):
        """ Run an iteration of the image search. """
        urls = []

        headers = {
            #'Host' : 'www.bing.com',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
            #'Cache-Control' : 'no-cache',
            #'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            #'Accept-Language' : 'en-US,en;q=0.9',
            'Cookie' : 'MUID=19E733ABCF5465DA11E33F41CB546693'
            #'Cookie': 'MMCA=ID=629B6B07AF87445AA899E90ABA4C9EDA; _IDET=NVNoti=1; ipv6=hit=1555870655622&t=4; MUID=19E733ABCF5465DA11E33F41CB546693; SRCHD=AF=B00032; SRCHUID=V=2&GUID=21D9F5CEC1A24DFC82D5A49E03D74266&dmnchg=1; _RwBf=s=70&o=18; ipv6=hit=1548138642686&t=4; MUIDB=19E733ABCF5465DA11E33F41CB546693; KievRPSSecAuth=FABiARRaTOJILtFsMkpLVWSG6AN6C/svRwNmAAAEgAAACFOMmMR1v9HPIAF4i2R0gK6Gka5wqlj4Pn9olKyS/gb9phXfMQNtvGDjoS/2m0jhHbvBQzdCJte0tTg60ev87v9V0dUEi7OP8J1DTugfDk/r3agNKFxvnWwp8LcAnrnKur4TZkBJ5qr904bWv2N256X601%2BLGbkF97cqshTXntq/WPPU51bVJy2HOkstK5FNmF8LqzL9sYlAsgWuvFTIiIzJm1JeOxz5b2iGk672CoEGXBLgp%2BYjKDmVUoUIp4J0eH/oJoQn0ZAbyoz304hQATAaL2KyVeSAvQWhY%2BCWc25tzCJZAVxUATTo//Eru8fFJRb6haxVbe24poHEXArH4XzmY3Ul%2BIIuFYxeqmCYk4yrw6XFSRYERW14nLhHbwkCAP0URa8aCQBwYNoUAIVR5Rg0klBGYJEKOBWKa%2Bt%2B6Min; PPLState=1; ANON=A=F40E25A36E0BF3A13CB8474FFFFFFFFF&E=1676&W=1; NAP=V=1.9&E=161c&C=HFzwSXtuyxYFCOtzYYm3Hobb5VYd7RN2hA76cJCziuqufCBBvkgjzw&W=1; _U=1ai3EWav_P9lsEWU97KSA_N5Yb71BDiSfHOxRlbujozrPuyJ9zi-WhbcKwg-jK9kSzvV1qr9xqWP6yWvsuNZpEU24TBgRqSpQif6aP5sznKsW7kWxZiZOyQ4cYi2fChMpq1zYdf6AwQyjN_U0gG3igLtuM2hklD4bcGmUjxi1-vCH13f__T3clp9gZ4X4HjLgzKdibdNg7KEXGGfC8SpLAA; WLS=C=2781e67b3d478360&N=Joshua; WLID=XBPfAfrCf7u9gNLBZQys/m/SoKf3W6nyFVwBizSP1QGomTt2kleyjw7zo8MJU27oeamkcMc/5NOOhxmLImzhB84Ht9ZeoSRB7lP6mRjuH5k=; _EDGE_S=mkt=en-us&ui=en-us&SID=1CF46CFC73DD68062DEE6010725F69FB; SRCHUSR=DOB=20190122&T=1555867054000&POEX=W; SRCHHPGUSR=CW=1635&CH=1154&DPR=1&UTC=-240&WTS=63691423314; _SS=SID=1CF46CFC73DD68062DEE6010725F69FB&R=40&RG=200&RP=35&RD=0&RM=0&RE=0&HV=1555867083'
            #accept-encoding: gzip, deflate, br
        }

        if not self._done:

            url = 'http://www.bing.com/images/search?q={}&first={}&count=35'.format(
                self._search_term,
                (self._page * 35) + 1
            )

            self._done = True
            self._page += 1

            req = requests.get(url, headers=headers)
            if req.status_code == 200:
                soup = BeautifulSoup(req.content, 'html.parser')
                anchors = soup.body.find_all('a')
                urls = [self._get_url(a) for a in anchors if self._is_image_anchor(a)]
                if len(urls) > 0:
                    self._done = False

        return urls


    def _get_url(self, a_tag):
        j = json.loads(a_tag['m'])
        print(j['murl'])

    def _is_image_anchor(self, a_tag):
        """ Test if the given anchor tag is a valid bing image thumbnail. """
        return a_tag.has_attr('m')


if __name__ == '__main__':
    s = ImageSearch()
    s.set_search_term('terminator')

    while True:
        urls = s.run()
        if len(urls) > 0:
            print(urls)
            break
