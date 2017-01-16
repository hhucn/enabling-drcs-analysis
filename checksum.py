#!/usr/bin/env python3

import argparse
import json
import hashlib
import os.path

import utils


def dict_checksum(obj):
    j = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(j.encode('utf-8')).hexdigest()


def file_checksum(fn):
    res = hashlib.sha256()
    with open(fn, 'rb') as f:
        for chunk in iter(lambda: f.read(2 ** 16), b''):
            res.update(chunk)
    return res.hexdigest()


def tree_checksums(root):
    if not root.endswith(os.sep):
        root += os.sep
    res = {}
    for dirpath, dirnames, files in os.walk(root):
        assert dirpath.startswith(root)
        dir_idx = dirpath[len(root):]

        for f in files:
            idx = (dir_idx + '/' + f) if dir_idx else f
            res[idx] = file_checksum(os.path.join(dirpath, f))
        for d in dirnames:
            idx = (dir_idx + '/' + d) if dir_idx else d
            res[idx] = '(directory)'

    return res


COMPONENTS = [
    ('config', lambda args: dict_checksum(args.config)),
    ('list', lambda _: dict_checksum(utils.read_data('list'))),
    ('repos', lambda _: dict_checksum(tree_checksums(os.path.join(utils.DATA_DIR, 'repos')))),
    ('prep', lambda _: dict_checksum(utils.read_data('sim_tasks'))),
]
COMPONENTS_MAP = {
    cname: cfunc
    for cname, cfunc in COMPONENTS
}


def main():
    parser = argparse.ArgumentParser('Show a checksum over the data')
    parser.add_argument(
        '-f', '--filter',
        metavar='COMPONENTS', default=None,
        help=((
            'Comma-separated list naming the components to be matched.' +
            ' Available components are %s') % ', '.join(cname for cname, _cfunc in COMPONENTS)))
    args = parser.parse_args()

    config = utils.read_config()
    args.config = config

    if args.filter:
        component_names = args.filter.split(',')
    else:
        component_names = [cname for cname, _ in COMPONENTS]

    for cname in component_names:
        cfunc = COMPONENTS_MAP.get(cname)
        if cfunc:
            cres = cfunc(args)
            print('%s: %s' % (cname, cres))
        else:
            raise Exception('Cannot find component %r to checksum' % cname)


if __name__ == '__main__':
    main()
