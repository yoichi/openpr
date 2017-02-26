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


if __name__ == '__main__':
    unittest.main()
