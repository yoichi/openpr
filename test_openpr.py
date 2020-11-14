#!/usr/bin/env python
import os
import shutil
import subprocess
import tempfile
import unittest

import openpr


def _call(args):
    # don't use subprocess.DEVNULL for python2.7
    with open(os.devnull, 'w') as devnull:
        subprocess.check_call(args, stdout=devnull, stderr=devnull)


class TempDir(object):
    def __enter__(self):
        self._directory = tempfile.mkdtemp()
        return self._directory

    def __exit__(self, *args):
        shutil.rmtree(self._directory)


class ChangeDir(object):
    def __init__(self, directory):
        self._new_cwd = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            directory)
        self._old_cwd = os.getcwd()

    def __enter__(self):
        os.chdir(self._new_cwd)

    def __exit__(self, *args):
        os.chdir(self._old_cwd)


class TestOpenpr(unittest.TestCase):
    def test_extract_service_and_module_gh_https(self):
        self.assertEqual(
            ('github.com', 'yoichi/openpr'),
            openpr.extract_service_and_module(
                'https://github.com/yoichi/openpr.git'))

    def test_extract_service_and_module_gh_https_without_extension(self):
        self.assertEqual(
            ('github.com', 'yoichi/openpr'),
            openpr.extract_service_and_module(
                'https://github.com/yoichi/openpr'))

    def test_extract_service_and_module_gh_with_trailing_slash(self):
        self.assertEqual(
            ('github.com', 'yoichi/openpr'),
            openpr.extract_service_and_module(
                'https://github.com/yoichi/openpr.git/'))
        self.assertEqual(
            ('github.com', 'yoichi/openpr'),
            openpr.extract_service_and_module(
                'https://github.com/yoichi/openpr/'))

    def test_extract_service_and_module_gh_ssh(self):
        self.assertEqual(
            ('github.com', 'yoichi/openpr'),
            openpr.extract_service_and_module(
                'git@github.com:yoichi/openpr.git'))

    def test_extract_service_and_module_bb_https(self):
        self.assertEqual(
            ('bitbucket.org', 'yoichi22/sandbox'),
            openpr.extract_service_and_module(
                'https://yoichi22@bitbucket.org/yoichi22/sandbox.git'))

    def test_extract_service_and_module_bb_ssh(self):
        self.assertEqual(
            ('bitbucket.org', 'yoichi22/sandbox'),
            openpr.extract_service_and_module(
                'git@bitbucket.org:yoichi22/sandbox.git'))

    def test_extract_pull_request_number_gh(self):
        self.assertEqual(
            '123',
            openpr.extract_pull_request_number(
                '0000000 Merge pull request #123 from foo/master\n'
                '1111111 Merge pull request #456 from bar/master'))

    def test_extract_pull_request_number_bb(self):
        self.assertEqual(
            '123',
            openpr.extract_pull_request_number(
                '0000000 Merged in foo/master (pull request #123)\n'
                '1111111 Merged in bar/master (pull request #456)'))

    def test_get_default_tracking_branch(self):
        """Detect default branch from remotes/origin/HEAD."""
        branch = 'trunk'
        with TempDir() as temp_dir:
            with ChangeDir(temp_dir):
                _call(['git', 'init', '--bare', 'foo_origin'])
                _call(['git', 'clone', 'foo_origin', 'foo_temp'])
            with ChangeDir(os.path.join(temp_dir, 'foo_temp')):
                _call(['git', 'checkout', '-b', 'trunk'])
                _call(['git', 'config', 'user.email', 'test@example.com'])
                _call(['git', 'config', 'user.name', 'test'])
                _call(['git', 'commit', '--allow-empty', '-m', 'message'])
                _call(['git', 'push', 'origin', branch])
            with ChangeDir(os.path.join(temp_dir, 'foo_origin')):
                _call(['git', 'symbolic-ref', 'HEAD',
                      'refs/heads/{}'.format(branch)])
            with ChangeDir(temp_dir):
                _call(['git', 'clone', 'foo_origin', 'foo'])
            with ChangeDir(os.path.join(temp_dir, 'foo')):
                remote = 'origin'
                self.assertEqual(openpr.get_default_tracking_branch(remote),
                                 '{}/{}'.format(remote, branch))

    def test_get_default_tracking_branch_fallback(self):
        """Without remotes/origin/HEAD, fallback to origin/master."""
        with TempDir() as temp_dir:
            with ChangeDir(temp_dir):
                _call(['git', 'init', '--bare', 'foo_origin'])
                _call(['git', 'clone', 'foo_origin', 'foo'])
            with ChangeDir(os.path.join(temp_dir, 'foo')):
                _call(['git', 'config', 'user.email', 'test@example.com'])
                _call(['git', 'config', 'user.name', 'test'])
                _call(['git', 'commit', '--allow-empty', '-m', 'message'])
                _call(['git', 'push', '-u', 'origin', 'master'])
                remote = 'origin'
                self.assertEqual(openpr.get_default_tracking_branch(remote),
                                 '{}/master'.format(remote))

    def test_get_remote_url(self):
        remote = 'bar'
        remote_url = 'foo_origin'
        with TempDir() as temp_dir:
            with ChangeDir(temp_dir):
                _call(['git', 'init', 'foo'])
            with ChangeDir(os.path.join(temp_dir, 'foo')):
                _call(['git', 'remote', 'add', remote, remote_url])
                self.assertEqual(openpr.get_remote_url(remote), remote_url)

    def test_get_pull_request_number(self):
        number = '123'
        with TempDir() as temp_dir:
            with ChangeDir(temp_dir):
                _call(['git', 'init', '--bare', 'foo_origin'])
                _call(['git', 'clone', 'foo_origin', 'foo'])
            with ChangeDir(os.path.join(temp_dir, 'foo')):
                _call(['git', 'config', 'user.email', 'test@example.com'])
                _call(['git', 'config', 'user.name', 'test'])
                _call(['git', 'commit', '--allow-empty', '-m', 'message'])
                _call(['git', 'checkout', '-b', 'feature'])
                _call(['git', 'commit', '--allow-empty', '-m', 'implement'])
                revision = subprocess.check_output(
                    ['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
                _call(['git', 'push', '-u', 'origin', 'feature'])
                _call(['git', 'checkout', 'master'])
                _call(['git', 'merge', '--no-ff', 'feature', '-m',
                       'Merge pull request #{} from feature'.format(number)])
                _call(['git', 'push', '-u', 'origin', 'master'])
                self.assertEqual(openpr.get_pull_request_number(revision,
                                                                'origin',
                                                                'master'),
                                 number)


if __name__ == '__main__':
    unittest.main()
