import errno
import itertools
import json
import math
import os.path
import re
import time


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


def iter_repos(parser, dirname, func):
    parser.add_argument(
        '-v', '--verbose',
        action='store_true', help='Show detailed status')
    parser.add_argument(
        '-q', '--no-status', dest='no_status',
        action='store_true', help='Do not show progress bars')
    parser.add_argument(
        '-f', '--filter',
        metavar='REGEXP', type=re.compile,
        help='Filter by repository fullname (regular expressions)')
    parser.add_argument(
        '-r', '--redo',
        action='store_true',
        help='Do this action even if it is marked complete for the repository')
    args = parser.parse_args()

    config = read_config()
    ignored_repos = set(config.get('ignored_repos', []))

    ensure_datadir(dirname)

    args.config = config

    def _should_visit(repo_dict):
        if repo_dict['full_name'] in ignored_repos:
            return False

        if args.filter and not args.filter.search(repo_dict['full_name']):
            return False

        if not args.redo:
            basename = safe_filename(repo_dict['full_name'])
            if data_exists(basename, dirname):
                return False

        return True

    initial_repos = list(read_data('list'))
    if not args.verbose and not args.no_status:
        msg = dirname.rstrip('/')
        initial_repos = progress.bar.Bar(msg).iter(initial_repos)
    for repo_dict in initial_repos:
        if not _should_visit(repo_dict):
            continue
        func(args, repo_dict)


def chunks(l, n):
    it = iter(l)
    while True:
        lst = list(itertools.islice(it, n))
        if not lst:
            break
        yield lst


def timestr(ts):
    return time.strftime('%Y%m%d_%H%M%S', time.localtime(ts))


def datestr(ts):
    return time.strftime('%Y-%m-%d', time.localtime(ts))


def evince(obj):
    print(json.dumps(obj, indent=2))


def time_func(func, args=[], kwargs={}):
    start = time.clock()
    res = func(*args, **kwargs)
    end = time.clock()
    print('That took %r seconds' % (end - start))
    return res


def percentile(percent, data):
    # From http://stackoverflow.com/a/2753343/35070
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    d0 = sorted_data[int(f)] * (c-k)
    d1 = sorted_data[int(c)] * (k-f)
    return d0+d1


class EmptyContextManager(object):
    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        pass
