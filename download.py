#!/usr/bin/env python3

import argparse
import os.path

import git

import utils


DIRNAME = 'repos/'


def download(args, repo_dict):
    basename = utils.safe_filename(repo_dict['full_name'])
    path = utils.calc_filename(basename, dirname=DIRNAME, suffix='')
    if os.path.exists(path) and not args.redo:
        return

    if args.verbose:
        print('Downloading %s ...' % repo_dict['html_url'])

    tmp_path = path + '.tmp'
    git.Repo.clone_from(repo_dict['git_url'], tmp_path, bare=True)
    os.rename(tmp_path, path)


def main():
    parser = argparse.ArgumentParser('Download the repositories')
    utils.iter_repos(parser, DIRNAME, download)


if __name__ == '__main__':
    main()
