.. _example-ref:

Using filabel in other applications
===================================
Regardless of that not being an intention and the code being written quite poorly, you can use parts of filabel's code in your own applications. There are not many functions that can be used in any application, however here are a few examples of what you can do. If you want to use any other function, you can read about the detailed functionality in :ref:`codedoc`.

.. testsetup::

   import filabel
   import os

   label_file = 'fixtures/labels.cfg'

You can for example use our label configuration file parsing function :func:`get_label_patterns()`:

.. testcode::

   with open(label_file) as f:
       d = filabel.github.get_label_patterns(f)
   print(d)

Which should give you a nice parsed dictionary (``{'rule': ['pattern1', 'pattern2', ...], ...}```):

.. testoutput::

   {'frontend': ['*/templates/*', 'static/*'], 'backend': ['logic/*'], 'docs': ['*.md', '*.rst', '*.adoc', 'LICENSE', 'docs/*'], 'file1': ['file1111111*'], 'file10': ['file10*'], 'file9': ['file9*']}


You can also use the function :func:`validate_repo_names()` for repository name validation:

.. doctest::

   >>> l = ['aaa/bbb', 'ccc']
   >>> filabel.cli.validate_repo_names(l)
   'ccc'

As you can see, the return value here is ``ccc`` because the second name (``ccc``) is not correct.

If you want to get the configuration files from the environment, there is a function :func:`get_conf_files()`:

.. testcode::

   os.environ['FILABEL_CONFIG'] = 'fixtures/credentials.cfg:fixtures/labels.cfg'
   r = filabel.web.get_conf_files()
   print(r)

Which should result in:

.. testoutput::

   {'cred': 'fixtures/credentials.cfg', 'label': 'fixtures/labels.cfg'}

If you want to get the label names that should be added to a list of files, you can do that by calling :func:`get_all_labels()`:

.. testcode::

   files = ['aaaa', "ahoj.md", "static/xyz", "file100", "file999"]
   with open(label_file) as f:
       patterns = filabel.github.get_label_patterns(f)
   l = filabel.github.get_all_labels(files, patterns)
   print(l)

The labeling rules (the same rules as in example on the configuration file parsing function) are all matched agaist the filenames and the output is a list of labels that should be used on the pull request with the current set of files:

.. testoutput::

   ['docs', 'frontend', 'file10', 'file9']