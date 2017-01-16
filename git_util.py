import io
import os
import utils


def setup():
	vhome = make_home_dir()
	os.environ['HOME'] = vhome


def make_home_dir():
	dn = utils.calc_filename('vhome', suffix='')
	utils.ensure_dir(dn)
	with io.open(os.path.join(dn, '.gitconfig'), 'w', encoding='utf-8') as gcf:
		gcf.write(
			'[user]\n' +
        	'name = Philipp Hagemeister\n' +
        	'email = phihag@phihag.de\n'
        )
	return dn
