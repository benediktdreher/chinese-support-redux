# Copyright © 2021 Benedikt Dreher <bdreher@fastmail.com>
# Inspiration: Thomas TEMPÉ, Joseph Lorimer
# License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/agpl.html

from os.path import basename, exists, join
from re import sub
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .hanzi import has_hanzi
from .main import config

import requests
from aqt import mw

requests.packages.urllib3.disable_warnings()

class StrokeOrderDownloader:
    def __init__(self, text, source='bishun'):
        self.text = text
        self.service = source
        self.path = self.get_path()
        self.func = {
            'bishun': self.get_bishun,
        }.get(self.service)

    def get_path(self):
        filename = '{}_{}.gif'.format(
            self.sanitize(self.text), self.service
        )
        return join(mw.col.media.dir(), filename)

    def sanitize(self, s):
        return sub(r'[/:*?"<>|]', '', s)

    def download(self):
        if exists(self.path):
            return basename(self.path)

        if not self.func:
            raise NotImplementedError(self.service)

        self.func()

        return basename(self.path)

    def get_bishun(self):
        query = {
            'q': self.text.encode('utf-8'),
        }

        url = 'http://bishun.strokeorder.info/mandarin.php?' + urlencode(query)
        request = Request(url)
        response = urlopen(request, timeout=5)

        if response.code != 200:
            raise ValueError('{}: {}'.format(response.code, response.msg))

        image_src = str(response.read())
        image_src = image_src.split('<img src="http://bishun.strokeorder.info/characters/')
        image_src = image_src[1].split('.gif')
        image_src = 'http://bishun.strokeorder.info/characters/' + image_src[0] + '.gif'

        request = Request(image_src)
        response = urlopen(request, timeout=5)

        if response.code != 200:
            raise ValueError('{}: {}'.format(response.code, response.msg))

        with open(self.path, 'wb') as image:
            image.write(response.read())

def strokeorder(hanzi, source=None):
    """Returns strokeorder tag for a given Hanzi string."""

    from .ruby import ruby_bottom, has_ruby

    if not has_hanzi(hanzi):
        return ''

    if not source:
        source = config['strokeorder']

    if not source:
        return ''

    if not hanzi:
        return ''

    if source:
        return '<img src="%s">' % StrokeOrderDownloader(hanzi, source).download()

    return ''