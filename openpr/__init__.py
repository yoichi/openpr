#!/usr/bin/env python
"""Find pull request from given commit hash and open it in a Web browser.

Depends on: git
Supported Services: GitHub, Bitbucket
"""

import argparse
import os
import re
import subprocess
import sys
import webbrowser

_pull_request_url = {
    'github.com': 'https://github.com/{module}/pull/{number}',
    'bitbucket.org': 'https://bitbucket.org/{module}/pull-requests/{number}',
}


def extract_service_and_module(repo_url):
    """Extract service and module from repository url.

    :param str repo_url: repository url

    :return (service, module)
    :rtype (str, str)
    """
    m = re.match(r'.+[/@]([^\.]+\.[^\.]+)[:/]([^/]+/[^/]+)\.git/?$', repo_url)
    if not m:
        m = re.match(r'.+[/@]([^\.]+\.[^\.]+)[:/]([^/]+/[^/]+)/?$', repo_url)
        if not m:
            raise Exception(
                'cannot detect service and module from {}'.format(repo_url))
    service = m.group(1)
    module = m.group(2)
    if service not in _pull_request_url.keys():
        raise Exception(
            'service not supported: {}'.format(service))
    return (service, module)


def _run_command(args):
    """Run command and get its output.

    :param list[str] args: command and arguments

    :return: output of the command
    :rtype: str

    :raise subprocess.CalledProcessError: command failed
    """
    return subprocess.check_output(
        args, stderr=subprocess.DEVNULL).strip().decode('utf-8')


def get_remote_url(remote):
    """Get remote repository url of current git repository.

    :param str remote: remote name against which pull requests are created

    :return: remote repository url
    :rtype: str
    """
    args = ['git', 'config', 'remote.{}.url'.format(remote)]
    return _run_command(args)


def extract_pull_request_number(commit_logs):
    """Extract first occurrence of pull request number from commit logs.

    :param str commit_logs: oneline commit logs

    :return: pull request number
    :rtype: str
    """
    m = re.search(r'pull request #(\d+)', commit_logs)
    if not m:
        raise Exception(
            'cannot detect pull request number from\n{}'.format(commit_logs))
    return m.group(1)


def get_default_tracking_branch(remote):
    """Get default remote branch of the current repository.

    detect by remote HEAD if present, or use "master" otherwise

    :param str remote: remote name

    :return: branch name
    :rtype: str
    """
    head = 'remotes/{}/HEAD'.format(remote)
    args = ['git', 'rev-parse', '--abbrev-ref', head]
    try:
        ref = _run_command(args)
        if ref == head:
            raise Exception
        return ref
    except Exception:
        return '{}/master'.format(remote)


def get_pull_request_number(revision, remote, base_branch):
    """Get pull request number from commit messages.

    :param str revision: revision string
    :param str remote: remote name against which pull requests are created
    :param str base_branch: branch against which pull request are merged

    :return: pull request number
    :rtype: str
    """
    if not re.match(r'^[0-9a-f]+$', revision):
        raise Exception('invalid revision: {}'.format(revision))
    if not base_branch:
        tracking_branch = get_default_tracking_branch(remote)
    else:
        tracking_branch = '{}/{}'.format(remote, base_branch)
    args = ['git', 'merge-base',
            '--is-ancestor',
            revision,
            tracking_branch]
    try:
        _run_command(args)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            raise Exception(
                '{revision} is not merged to {tracking_branch} yet'.format(
                    **{'revision': revision,
                       'tracking_branch': tracking_branch}))
        raise
    args = ['git', 'log',
            '--merges', '--oneline', '--reverse', '--ancestry-path',
            '{revision}...{tracking_branch}'.format(
                **{'revision': revision, 'tracking_branch': tracking_branch})]
    output = subprocess.check_output(args).decode('utf-8')
    return extract_pull_request_number(output)


def get_pull_request_url(service, module, number):
    """Get pull-request URL.

    :param str service: service name
    :param str module: module path ('owner/repo')
    :param int number: pull-request identification number
    """
    if service not in _pull_request_url:
        raise Exception(
            'service not supported: {}'.format(service))
    url = _pull_request_url[service]
    return url.format(**{'module': module, 'number': number})


def openpr(revision, base_branch, remote, print_only):
    """Find pull request from given commit hash and open it in a Web browser.

    :param str revision: revision string of the target commit
    :param str remote: remote name against which pull requests are created
    :param str base_branch: branch against which pull requests are merged
    :param bool print_only: print pull request url instead of opening it
    """
    number = get_pull_request_number(revision, remote, base_branch)
    repo_url = get_remote_url(remote)
    (service, module) = extract_service_and_module(repo_url)
    pr_url = get_pull_request_url(service, module, number)
    if print_only:
        print(pr_url)
    else:
        webbrowser.open(pr_url)


def main():
    """Parse command line arguments and call openpr()."""
    parser = argparse.ArgumentParser(
        description='Find pull request from given commit hash and open it in a Web browser.')
    parser.add_argument(
        'revision',
        help='revision string of the target commit')
    parser.add_argument(
        '-b', '--base-branch',
        metavar='BRANCH',
        default='',
        help=('branch against which pull requests are merged (default: detect by remote HEAD if '
              'present, or use "master" otherwise'))
    parser.add_argument(
        '-r', '--remote',
        default='origin',
        help='remote name against which pull requests are created (default: origin)')
    parser.add_argument(
        '-p', '--print-only',
        action='store_true',
        help='print pull request url instead of opening it')
    args = parser.parse_args()
    try:
        openpr(args.revision, args.base_branch, args.remote, args.print_only)
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(-1)


if __name__ == '__main__':
    main()
