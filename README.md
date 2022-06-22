# GitHub action for setting up Python and running tox.

It tests a package on multiple Python versions using tox.
Works best with ``tox-gh-actions``.

We expect that tox sets up a buildout, so we set up an egg cache for it.
If buildout is not used, the egg cache is useless, but should be harmless.

Created by Maurits van Rees.
Currently trying this out in https://github.com/zestsoftware/collective.multisearch/pull/6

# Simple example

This is copied from the files in this repository that we use to test the action itself.
We test two Python versions.
For each version we run one tox environment.
We simply call `python test.py`.

## .github/workflows/tests.yml

```
name: CI
on:
  push:
    branches:
      - "main"
  pull_request:
  workflow_dispatch:
jobs:
  test:
    name: Run tests
    runs-on: ubuntu-latest
    strategy:
      fail-fast: true
      matrix:
        python-version: ["3.9", "3.10"]
    steps:
      - name: Test Py ${{ matrix.python-version }}
        uses: collective/tox-action@main
        with:
          python-version: ${{ matrix.python-version }}
```

## tox.ini

**Important**: You **MUST** have a `gh-actions` section, otherwise no tests are run.
You will see `Run tox --skip-missing-interpreters=false` and then nothing. The job will be marked as success, but no tests will have been run.

```
# Tox file so we can test ourselves.
[tox]
envlist = py{39,310}
skip_missing_interpreters = True

[gh-actions]
# See https://pypi.org/project/tox-gh-actions/
python =
    3.9: py39
    3.10: py310

[testenv]
skip_install = true
commands = python test.py
```

## requirements.txt

Our action uses a pip cache from `actions/setup-python`.
This fails when the `requirements.txt` file is missing.
So you must have this file, but in our example it is empty.


# Advanced example

In this example we will test Plone 5.2 and Plone 6 using Buildout on Python 2.7 and various Python 3 versions.
See this [`collective.multisearch` PR](https://github.com/zestsoftware/collective.multisearch/pull/6) that adds the yaml file.

## .github/workflows/tests.yml

Use this action and pass it the list of Python versions with which you want to test.

```
name: CI
on:
  push:
    branches:
      - "main"
  pull_request:
  workflow_dispatch:
jobs:
  test:
    name: Run tests
    runs-on: ubuntu-latest
    strategy:
      fail-fast: true
      matrix:
        python-version: ["2.7", "3.6", "3.7", "3.8", "3.9"]
    steps:
      - name: Test Py ${{ matrix.python-version }}
        uses: collective/tox-action@main
        with:
          python-version: ${{ matrix.python-version }}
```

## tox.ini

This has three sections.

- `tox`:
  Here we define tox environments for two Plone versions.
- `gh-actions`:
   This is  a mapping from Python version to tox environments.
   `3.8: py38` means: on Python `3.8`, run all tox environments that have `py38` in their name: `plone52-py38` and `plone60-py38`.
- `testenv`:
   This is a test setup that works for me:
   - Have one buildout config file per Plone version.  They likely extend a shared `base.cfg` to avoid duplication.
   - Use one `requirements.txt` for all environments, pinning `zc.buildout` and `setuptools`.
   - Let Buildout install only the `test` part, so *not* for example `instance`, `omelette`, `code-analysis`.
   - Finally, run `bin/test`.

```
[tox]
envlist =
    plone52-py{27,36,37,38}
    plone60-py{37,38,39}
skip_missing_interpreters = True

[gh-actions]
# See https://pypi.org/project/tox-gh-actions/
python =
    2.7: py27
    3.6: py36
    3.7: py37
    3.8: py38
    3.9: py39

[testenv]
setenv =
    plone52: version_file=test-5.2.x.cfg
    plone60: version_file=test-6.0.x.cfg
skip_install = true
deps =
    -rrequirements.txt
commands_pre =
    {envbindir}/buildout -c {toxinidir}/{env:version_file} buildout:directory={envdir} buildout:develop={toxinidir} install test
commands =
    {envbindir}/test {posargs:-vc}
```

## requirements.txt

If you need Python 2.7, this should work best:

```
# Keep in sync with base.cfg please.
zc.buildout==2.13.7
setuptools==42.0.2
wheel
```

If you only need to support Python 3, `zc.buildout` 3 with latest `setuptools` should work fine too.

## base.cfg

```
[buildout]
package-name = collective.multisearch
# If you have a test extra in setup.py/cfg, specify it here:
# package-extras = [test]

[versions]
# It is easiest to use the same zc.buildout and setuptools versions for all.
# Keep in sync with requirements.txt please.
zc.buildout = 2.13.7
setuptools = 42.0.2
```

## test-5.2.x.cfg

```
[buildout]
extends =
    https://raw.githubusercontent.com/collective/buildout.plonetest/master/test-5.2.x.cfg
    base.cfg
```

## test-6.0.x.cfg

```
[buildout]
extends =
    https://raw.githubusercontent.com/collective/buildout.plonetest/master/test-6.0.x.cfg
    base.cfg
```
