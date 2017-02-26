#!/usr/bin/env python
"""Find pull request from given commit hash and open it in a Web browser.

Depends on: git
Supported Services: GitHub, Bitbucket
"""

import argparse
import commands
import re
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
    m = re.match('.+[/@]([^\.]+\.[^\.]+)[:/]([^/]+/[^/]+)\.git$', repo_url)
    if not m:
        raise Exception(
            'cannot detect service and module from {0}'.format(repo_url))
    service = m.group(1)
    module = m.group(2)
    if service not in _pull_request_url.keys():
        raise Exception(
            'service not supported: {0}'.format(service))
    return (service, module)


def _run_command(command):
    """Run a command.

    :return: command output
    :rtype: str
    """
    (status, output) = commands.getstatusoutput(command)
    if status != 0:
        raise Exception('"{0}" failed: {1}'.format(command, status))
    return output


def get_remote_url():
    """Get remote repository url of current git repository.

    :return: remote repository url
    :rtype: str
    """
    return _run_command('git remote get-url origin')


def get_pull_request_number(revision, base_branch):
    """Get pull request number from commit messages.

    :param str revision: revision string
    :param str base_branch: branch against which pull request are merged

    :return: pull request number
    :rtype: str
    """
    if not re.match('^[0-9a-f]+$', revision):
        raise Exception('invalid revision: {0}'.format(revision))
    command = 'git log {options} {revision}...{base_branch}'.format(
        **{'options': '--merges --oneline --reverse --ancestry-path',
           'revision': revision,
           'base_branch': base_branch})
    output = _run_command(command)
    m = re.search('pull request #(\d+)', output)
    if not m:
        raise Exception(
            'cannot detect pull request number by {0}'.format(command))
    return m.group(1)


def get_pull_request_url(service, module, number):
    """Get pull-request URL.

    :param str service: service name
    :param str module: module path ('owner/repo')
    :param int number: pull-request identification number
    """
    if service not in _pull_request_url:
        raise Exception(
            'service not supported: {0}'.format(service))
    url = _pull_request_url[service]
    return url.format(**{'module': module, 'number': number})


def main(revision, base_branch, print_only):
    """Find pull request from given commit hash and open it in a Web browser.

    :param str revision: revision string of the target commit
    :param str base_branch: branch against which pull requests are merged
    :param bool print_only: print pull request url instead of opening it
    """
    number = get_pull_request_number(revision, base_branch)
    repo_url = get_remote_url()
    (service, module) = extract_service_and_module(repo_url)
    pr_url = get_pull_request_url(service, module, number)
    if print_only:
        print(pr_url)
    else:
        webbrowser.open(pr_url)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Find pull request from given commit hash and open it in a Web browser.')
    parser.add_argument(
        'revision',
        help='revision string of the target commit')
    parser.add_argument(
        '--base-branch',
        metavar='BRANCH',
        default='master',
        help='branch against which pull requests are merged (default: master)')
    parser.add_argument(
        '--print-only',
        action='store_true',
        help='print pull request url instead of opening it')
    args = parser.parse_args()
    try:
        main(args.revision, args.base_branch, args.print_only)
        sys.exit(0)
    except Exception as e:
        print(e.message)
        sys.exit(-1)
