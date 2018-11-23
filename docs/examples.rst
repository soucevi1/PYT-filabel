.. _example-ref:

Using filabel in other applications
===================================
Regardless of that not being an intention, you can use parts of filabel's code in applications that you write. Here are a few examples of what you can do. You can read about the detailed functionality in :ref:`codedoc`.

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