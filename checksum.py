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


def print_checksum(args):
    print('config: %s' % dict_checksum(args.config))
    print('list: %s' % dict_checksum(utils.read_data('list')))

    repos_dir = os.path.join(utils.DATA_DIR, 'repos')
    print('repos: %s' % dict_checksum(tree_checksums(repos_dir)))

    print('sim preparation: %s' % dict_checksum(utils.read_data('sim_tasks')))


def main():
    parser = argparse.ArgumentParser('Show a checksum over the data')
    args = parser.parse_args()

    config = utils.read_config()
    args.config = config

    print_checksum(args)


if __name__ == '__main__':
    main()
