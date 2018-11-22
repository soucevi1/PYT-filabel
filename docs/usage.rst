How to use filabel?
===================

This section will show you all the possible usages of the program.

.. _auth-ref:

Authorization used by filabel
----------------------------------------------

GitHub obviously requires you to authorize before allowing you to make any requests to its API (getting information about pull requests, adding labels...). 

In order for filabel to work you need to generate your `GitHub security token <https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/>`_. 

**Be careful not to make the token public!** The token is your secret, GitHub only shows it to you once after the generation, so just copy paste it into a configuration file (explained later) and do not upload the file anywhere.

The token is required for both CLI and web usage of the application.

.. _prep-ref:

What to prepare before running filabel
--------------------------------------

As we told you in the previous section, you need to geneate the Github security token. You pass the token to filabel using a configuration file.

You actually need to crate two configuration files. One that will contain the credentials and the other one that will contain the labeling rules. Both configuration files must be in the `configparser <https://docs.python.org/3/library/configparser.html>`_ format.

The configuration file with credentials (name it any way you want) must always contain ``[github]`` header and your GitHub security token. 

.. code-block:: none

   [github]
   token=<PASTE YOUR TOKEN HERE>

If you want to use filabel as a web application, you muset include your webhook secret as well (more about webhooks later). The required form of the credentials congifuration file is:

.. code-block:: none

   [github]
   token=<PASTE YOUR TOKEN HERE>
   secret=<PASTE YOUR WEBHOOK SECRET HERE>


The other configuration file must contain labeling rules. These are the rules that will be applied while labeling your pull requests. They contain the label name and a list of rules for `fnmatch <https://docs.python.org/3.4/library/fnmatch.html>`_ that will be matched against the filenames contained in the pull request. 

Let's say we want filabel to use label ``frontend`` on pull requests changing the files in ``templates`` and ``static`` directories, label ``backend`` on pull requests changing the files in the ``logic`` directory and label ``docs`` on pull requests changing the files in the ``docs`` directory and also files with ``*.rst`` suffix.
The required form of the configuration file is:

.. code-block:: none

   [labels]
   frontend=
       */templates/*
       static/*
   backend=logic/*
   docs=
       *.rst
       docs/*



