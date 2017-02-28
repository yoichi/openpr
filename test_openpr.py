#!/usr/bin/env python
import unittest

import openpr


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


if __name__ == '__main__':
    unittest.main()
