import itertools
import json
import re
import time
import urllib.parse
import sys

import requests

import utils


def build_url(path, params=None):
    if path.startswith('/'):
        base = 'https://api.github.com' + path
    else:
        base = path
    assert base.startswith('https://api.github.com')

    config = utils.read_config()
    params = {} if params is None else params.copy()
    params['client_id'] = config['client_id']
    params['client_secret'] = config['client_secret']
    q = ('&' if ('?' in path) else '?') + urllib.parse.urlencode(params)
    url = base + q
    return url


def query(path, params=None):
    while True:
        url = build_url(path, params)
        if utils.read_config().get('verbose'):
            print(url)
        r = requests.get(url)
        if r.status_code == 403 and 'X-RateLimit-Reset' in r.headers:
            reset = int(r.headers['X-RateLimit-Reset'])
            wait = max(0, reset - time.time()) + 60
            sys.stderr.write('Reached API rate limit. Waiting %d seconds ...\n' % wait)
            assert wait < 6 * 3600
            time.sleep(wait)
            continue
        if r.status_code != 200:
            raise Exception('Status %d: %s' % (r.status_code, r.text))
        break
    return (r, json.loads(r.text))


def paged(path, params=None, limit=None, get_items=None):
    yielded = 0
    while True:
        r, data = query(path, params)
        items = get_items(data) if get_items else data
        link = r.headers.get('Link', '')
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
