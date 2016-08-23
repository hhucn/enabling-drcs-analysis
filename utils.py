import errno
import json
import os.path
import re


import progress.bar  # if this fails: pip3 install progress
import progress.spinner


def read_json(fn):
	with open(fn) as f:
		return json.load(f)


def write_json(fn, data):
	with open(fn, 'w') as f:
		json.dump(data, f, indent='\t')


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def ensure_dir(dn):
	try:
		os.mkdir(DATA_DIR)
	except OSError as ose:
		if ose.errno != errno.EEXIST:
			raise ose


def ensure_datadir(subname):
	ensure_dir(os.path.join(DATA_DIR, subname))

def read_data(basename):
	fn = os.path.join(DATA_DIR, basename + '.json')
	return read_json(fn)

def write_data(basename, data):
	if not re.match(r'^[a-z0-9A-Z_-]+$', basename):
		raise Exception('Invalid basename %r' % basename)
	ensure_dir(DATA_DIR)

	fn = os.path.join(DATA_DIR, basename + '.json')
	write_json(fn, data)


def parse_repo_name(url):
	m = re.match('^https://api.github.com/repos/([^/]+)/([^/]+)', url)
	assert m
	return (m.group(1), m.group(2))


def progress_list(generator, count=None):
	pb = progress.bar.Bar(max=count) if count else progress.spinner.Spinner()
	return list(pb.iter(generator))
