openpr
======

Find pull request from given commit hash and open it in a Web browser.

## Description

Software development process sometimes stores useful information in the pull
request in which commits were reviewed and merged. On debugging a software,
we might be helped by such information in addition to source codes and commit
messages stored in the repository.

This utility enable you to open pull request page quickly from the commit hash
obtained by git blame.

## Requirement

* local repository (its remote points to GitHub or Bitbucket)
* Python 2.7 or Python 3
* git

## Installation

	pip install openpr

## Usage

Run as follows in the working tree

	openpr [-h] [-b BRANCH] [-r REMOTE] [-p] revision

## License

BSD-2-Clause

## Author

[yoichi](https://github.com/yoichi)