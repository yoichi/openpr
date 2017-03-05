#!/usr/bin/env python
import os
import shutil
import subprocess
import tempfile
import unittest

import openpr


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
        call = subprocess.call
        with TempDir() as temp_dir:
            with ChangeDir(temp_dir):
                call(['git', 'init', '--bare', 'foo_origin'])
                call(['git', 'clone', 'foo_origin', 'foo_temp'])
            with ChangeDir(os.path.join(temp_dir, 'foo_temp')):
                call(['git', 'checkout', '-b', 'trunk'])
                call(['git', 'commit', '--allow-empty', '-m', 'message'])
                call(['git', 'push', 'origin', branch])
            with ChangeDir(os.path.join(temp_dir, 'foo_origin')):
                call(['git', 'symbolic-ref', 'HEAD',
                      'refs/heads/{}'.format(branch)])
            with ChangeDir(temp_dir):
                call(['git', 'clone', 'foo_origin', 'foo'])
            with ChangeDir(os.path.join(temp_dir, 'foo')):
                remote = 'origin'
                self.assertEqual(openpr.get_default_tracking_branch(remote),
                                 '{}/{}'.format(remote, branch))

    def test_get_default_tracking_branch_fallback(self):
        """Without remotes/origin/HEAD, fallback to origin/master."""
        call = subprocess.call
        with TempDir() as temp_dir:
            with ChangeDir(temp_dir):
                call(['git', 'init', '--bare', 'foo_origin'])
                call(['git', 'clone', 'foo_origin', 'foo'])
            with ChangeDir(os.path.join(temp_dir, 'foo')):
                call(['git', 'commit', '--allow-empty', '-m', 'message'])
                call(['git', 'push', '-u', 'origin', 'master'])
                remote = 'origin'
                self.assertEqual(openpr.get_default_tracking_branch(remote),
                                 '{}/master'.format(remote))


if __name__ == '__main__':
    unittest.main()
