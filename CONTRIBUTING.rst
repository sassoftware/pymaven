How To Contribute
=================

Thank you for considering contributing to ``pymaven``.
Please read our `Contributor's Agreement`_ first.
Some things we would like you to know:

- There's no such thing as a contribution that is "too small".
  Grammar and spelling corrections are just as important as fixing bugs or adding features.
- Each pull request should focus on one change.
  This makes them easier to review and merge.
- Tests are required for all changes.
  If you fix a bug, add a test to ensure that bug stays fixed.
- New features require new documentation.
- ``pymaven``'s API is still considered in flux, but API breaking changes need to clear a higher bar than new features.
- Pull requests that do not pass our CI_ checks will not receive feedback.
  If you need help passing the CI_ checks, add the ``CI Triage`` label to your pull request.
- ``pymaven`` adheres to the `conventional commits <https://www.conventionalcommits.org/en/v1.0.0/>`_ standard for commit messages.
  In addition, you may want to read `How to Write a Git Commit Message <https://chris.beams.io/posts/git-commit/>`_.


Code Style
----------

``pymaven`` uses the black_ and isort_ formatters to ensure consistency in code format.

The ``tox -e lint`` command will run our pre-commit_ hooks.
Please run these before creating your pull request to save yourself wasted time.


Tests
-----

``pymaven`` is in the process of migrating to pure pytest_.
New tests should either go into a new test class, or into an existing test class that does not inherit from ``unittest.TestCase``.
You can earn extra brownie points by migrating old tests that exercise code you changed.

When writing tests, some guidelines that we suggest you follow are:

- Use the variables ``want`` and ``got`` to hold data for assertions, and write your assertions ``want == got``:

  .. code-block:: python

     x = f()
     want = 42
     got = x.some_attribute

     assert want == got

- Generally, one assertion per test. If you need to test multiple variables, then compare two tuples:

  .. code-block:: python

     x = Foo()
     got = (x.first_name, x.last_name)
     want = ("Alice", "Smith")
     assert want == got

- Use tox_ to run the test suite.
  This ensures that your tests are run in the same way as our CI_.
- New public APIs, or changes to existing ones, should be added to the type stubs (``.pyi`` files).


Documentation
-------------

- ``pymaven`` uses `semantic newlines`_ in reStructuredText_ files:

  .. code-block:: rst

     This is a sentence.
     This is another sentence.

- Sections should be separated by two lines, unless there is no content between one section header and the next:

  .. code-block:: rst

     Lorem Ipsum
     -----------

     Lorem ipsum dolor sit amet, consectetur adipiscing elit.
     Phasellus iaculis tempor iaculis.


     Morbi Consectetur
     -----------------

     Phasellus Aliquet
     ^^^^^^^^^^^^^^^^^

     Phasellus aliquet luctus dolor, vel auctor justo mattis vitae.


Changelog
^^^^^^^^^

All changes should include a changelog entry.
To make this easier ``pymaven`` uses the towncrier_ package to manage our ``CHANGELOG.rst`` file.
Unless you are helping cut a new release of ``pymaven``, you won't need to run ``towncrier`` yourself.
Instead, add a single file to the ``changelog.d`` directory as part of your pull request named ``<pull request #>.(breaking|build|chore|deprecation|feat|fix|tests).rst``.

Changelog entries should follow these rules:

- Use `semantic newlines`_, just like other documentation.
- Wrap the names of things in double backticks, ``like this``.
- Wrap arguments with asterisks: *these* or *attributes*.
- Names of functions or other callables should be followed by parentheses, ``my_cool_function()``.
- Use the active voice and either present tense or simple past tense.

  + Added ``my_cool_function()`` to do cool things.
  + Creating ``Foo`` objects with the *many* argument no longer raises a ``RuntimeError``.

- For changes that address multiple pull requests, create multiple fragments with the same contents.

To see what ``towncrier`` will add to the ``CHANGELOG.rst``, run ``tox -e changelog``.


Development
-----------

First, make a fork of the ``pymaven`` repository by going to https://github.com/sassoftware/pymaven and clicking on the **Fork** button near the top of the page.

Then clone your fork of the ``pymaven`` repository:

.. code-block:: bash

    $ git clone git@github.com:<username>/pymaven.git

Like most python projects, ``pymaven`` developers will want to  create a virtual environment.
The simplest method to create a virtual environment is:

.. code-block:: bash

    $ python3.8 -m venv --prompt=pymaven venv
    $ source venv/bin/activate

Beyond this simple setup there are some tools that help with managing virtual environments:

- `virtualenvwrapper <https://virtualenvwrapper.readthedocs.io/>`_
- `virtualfish <https://virtualfish.readthedocs.io/>`_
- `pyenv-virtualenv <https://github.com/pyenv/pyenv-virtualenv>`_

``pyenv-virtualenv`` is particularly convenient, since you will probably need to use pyenv_ to manage installing multiple python versions.

Once you have created and **activated** your virtualenv, you can install ``pymaven`` in development mode by running:

.. code-block:: bash

    $ pip install -e '.[dev]'

To verify everything is working, run:

.. code-block:: bash

   $ python -m pytest
   $ cd docs
   $ make html

which should output html docs in ``docs/_build/html/``.

Installing the pre-commit_ hooks is recommend to ensure your commit will pass our CI checks:

.. code-block:: bash

   $ pre-commit install


.. _CI: https://github.com/sassoftware/pymaven/actions?query=workflow%3ACI
.. _Contributor's Agreement: https://github.com/sassoftware/pymaven/blob/master/ContributorAgreement.txt
.. _black: https://github.com/psf/black
.. _isort: https://github.com/timothycrosley/isort
.. _pre-commit: https://pre-commit.com/
.. _pyenv: https://github.com/pyenv/pyenv
.. _pytest: https://docs.pytest.org/en/latest/
.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _semantic newlines: https://rhodesmill.org/brandon/2012/one-sentence-per-line/
.. _towncrier: https://pypi.org/project/towncrier
.. _tox: https://tox.readthedocs.io/
