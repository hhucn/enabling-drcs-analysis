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


def check_unlocked(basepath):
    lock_fn = os.path.join(basepath, '.git', 'index.lock')
    if os.path.exists(lock_fn):
        raise Exception('Lockfile %s still exists!' % lock_fn)


def rm_gitcrap(basepath):
    for dirpath, dirnames, filenames in os.walk(basepath, topdown=True):
        if '.git' in dirnames:
            dirnames.remove('.git')
        if '.gitmodules' in filenames:
            os.unlink(os.path.join(dirpath, '.gitmodules'))
