import errno
import json
import os.path


def read_json(fn):
	with open(fn) as f:
		return json.load(f)


def write_json(fn, data):
	with open(fn, 'w') as f:
		json.dump(data, f, indent='\t')


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def write_data(basename, data):
	try:
		os.mkdir(DATA_DIR)
	except OSError as ose:
		if ose.errno != errno.EEXIST:
			raise ose

	fn = os.path.join(DATA_DIR, basename + '.json')
	write_json(fn, data)
