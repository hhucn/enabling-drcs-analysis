import errno
import itertools
import json
import os.path
import re


import progress.bar  # if this fails: pip3 install progress
import progress.spinner


def read_json(fn):
    with open(fn) as f:
        return json.load(f)


def write_json(fn, data):
    with open(fn + '.tmp', 'w') as f:
        json.dump(data, f, indent='\t')
    os.rename(fn + '.tmp', fn)


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def ensure_dir(dn):
    try:
        os.mkdir(dn)
    except OSError as ose:
        if ose.errno != errno.EEXIST:
            raise ose


def ensure_datadir(subname):
    ensure_dir(os.path.join(DATA_DIR, subname))


def read_data(basename, dirname=None):
    fn = calc_filename(basename, dirname)
    return read_json(fn)


def calc_filename(basename, dirname=None, suffix='.json'):
    if not re.match(r'^[.a-z0-9A-Z_-]+$', basename):
        raise Exception('Invalid basename %r' % basename)

    if dirname:
        return os.path.join(DATA_DIR, dirname, basename + suffix)
    else:
        return os.path.join(DATA_DIR, basename + suffix)


def data_exists(basename, dirname=None):
    return os.path.exists(calc_filename(basename, dirname))


def write_data(basename, data, dirname=None):
    ensure_dir(DATA_DIR)

    write_json(calc_filename(basename, dirname), data)


def progress_list(generator, count=None):
    pb = progress.bar.Bar(max=count) if count else progress.spinner.Spinner()
    return list(pb.iter(generator))


def _read_config():
    config_fn = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'config.json')
    return read_json(config_fn)


_config = _read_config()


def read_config():
    return _config


def safe_filename(n):
    res = re.sub(r'[^.a-zA-Z0-9_-]+', '___', n)
    assert re.match(r'^[.a-zA-Z0-9_-]+$', res), \
        ('%r is not a safe filename' % res)
    return res


def iter_repos(parser, msg, func):
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed status')
    parser.add_argument('-q', '--no-status', action='store_true', help='Do not show progress bars')
    args = parser.parse_args()

    config = read_config()
    ignored_repos = set(config.get('ignored_repos', []))

    initials = read_data('list')
    if not args.verbose and not args.no_status:
        initials = progress.bar.Bar(msg).iter(initials)
    for irepo in initials:
        if irepo['full_name'] in ignored_repos:
            continue
        func(irepo, args.verbose)


def chunks(l, n):
    it = iter(l)
    while True:
        lst = list(itertools.islice(it, n))
        if not lst:
            break
        yield lst
