import itertools
import json
import re
import urllib.parse

import requests

import utils


def build_url(path, params=None):
    assert path.startswith('/')
    config = utils.read_config()
    params = {} if params is None else params.copy()
    params['client_id'] = config['client_id']
    params['client_secret'] = config['client_secret']
    q = ('&' if ('?' in path) else '?') + urllib.parse.urlencode(params)
    url = 'https://api.github.com' + path + q
    return url


def query(path, params=None):
    url = build_url(path, params)
    if utils.read_config().get('verbose'):
        print(url)
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception('Status %d: %s' % (r.status_code, r.text))
    return (r, json.loads(r.text))


def paged(path, params=None, limit=None, get_items=None):
    yielded = 0
    while True:
        r, data = query(path, params)
        link = r.headers['Link']
        items = get_items(data) if get_items else data
        m = re.search('<https://api\.github\.com([^>]+)>;\s*rel="next"', link)
        if limit is not None:
            if yielded + len(items) >= limit:
                yield from itertools.islice(items, limit - yielded)
                return

        yield from items
        yielded += len(items)
        if not m:
            break
        path = m.group(1)