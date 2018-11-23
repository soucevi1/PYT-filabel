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


One day we might actually stop being lazy and make our `GitHub repository <https://github.com/soucevi1/PYT-01>`_ public. In that case, you can clone the repository on your computer, switch into its directory and install it by running:

.. code-block:: none

   $ python setup.py sdist
   $ python -m pip install dist/filabel_soucevi1-version.tar.gz

Where ``version`` in the filename is the version of the release.


Building the documentation
--------------------------

In order to build the docs, you need to install `Sphinx <http://www.sphinx-doc.org/en/master/>`_ (together with doctest and autodoc if you want to change the program functionality).

To generate the documentation, just switch to the `docs` directory and run 

.. code-block:: none

   $ make html

To run the `doctest`, simply run

.. code-block:: none

   $ make doctest

All the documentation is written in `reStructuredText <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html>`_ format.

