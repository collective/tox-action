# GitHub action for setting up Python and running tox.

It tests a package on multiple Python versions using tox.
Works best with ``tox-gh-actions``.

We expect that tox sets up a buildout, so we set up an egg cache for it.
If buildout is not used, the egg cache is useless, but should be harmless.

Created by Maurits van Rees.
Currently trying this out in https://github.com/zestsoftware/collective.multisearch/pull/6
