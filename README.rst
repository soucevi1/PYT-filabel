soucevi1-filabel
================

CLI and web application that automatically adds labels to GitHub pull requests.
The labels are determined according to changed files in the pull request and
given configuration file.

Installation
------------

The program is currently only uploaded on `Testing PyPI <https://test.pypi.org/project/filabel-soucevi1/>`_. You can install filabel (with all its dependencies) from there using:

.. code-block:: none

   $ python -m pip install --extra-index-url https://test.pypi.org/pypi filabel-soucevi1


You can also get the program straight from our `GitHub repository <https://github.com/soucevi1/PYT-01>`_. In that case, you can clone the repository on your computer, switch into its directory and install it by running:

.. code-block:: none

   $ python setup.py install

You can also create `sdist` or `bdist`

.. code-block:: none 

   $ python setup.py sdist
   $ python setup.py bdist_wheel


Building the documentation
--------------------------

In order to build the docs, you need to install `Sphinx <http://www.sphinx-doc.org/en/master/>`_ (together with ``doctest`` and ``autodoc`` if you want to change the program functionality).

To run the `doctest`, simply switch to ``docs`` directory and run

.. code-block:: none

   $ make doctest

To get the API documentation, switch to the project root directory and run

.. code-block::

   $ python -m sphinx.apidoc -o docs filabel

To generate the documentation, just switch back to the ``docs`` directory and run 

.. code-block:: none

   $ make html

In order to pass the ``doctest`` tests you need to create files ``docs/fixtures/labels.cfg`` (containing the labeling rules) and ``docs/fixtures/credentials.cfg`` (containing the GitHub token)

All the documentation is written in `reStructuredText <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html>`_ format.



