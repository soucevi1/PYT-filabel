.. soucevi1-filabel documentation master file, created by
   sphinx-quickstart on Wed Nov 21 18:16:42 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation of Filabel
============================================

Filabel is a Python package for automatic labeling of GitHub pull requests.

It has two modes of operation: cli and web.

What does the cli mode do?
------------------------------
Let's say you have a GitHub repository called myrepo and you want to automatically label all the pull requests that change files with the extensions *.rst* (let's label them ``docs``) and *.py* (we will label them ``code``).

All you have to do is create two configuration files. One of them will contain the rules for labeling, let's call it ``lab.cfg``. The contents should look like this::

   [labels]
   docs=
       *.rst
   code=
       *.py

The other configuration file (we will name it ``cred.cfg``) should contain your credentials. Be careful not to make it public anywhere. ::

   [github]
   token=<YOUR GITHUB TOKEN>
   secret=<YOUR WEBHOOK SECRET>

You can read about the token and the secret in :ref:`auth-ref`. Once you have the configuration files, all you need now is the name of your github repository (i.e. ``myuser/myrepo``). Then you can call::

   python -m filabel -a cred.cfg -l lab.cfg myuser/myrepo

And the program will start labeling your pull requests. The output should look like this::

   REPO myuser/myrepo - OK
       PR https://github.com/myuser/myrepo/pull/4 - OK
           + code
       PR https://github.com/myuser/myrepo/pull/2 - OK
           - code
           + docs

How about the web application?
------------------------------
The web application does basically the same thing as the cli module. You just deploy it on your favorite domain and set a webhook (see :ref:`webhook-ref`) on it. Then, after a pull request is made on your repository, GitHub contacts the application via the webhook and the pull request is labeled instantly.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   cliusage
   webusage
   modules
   examples



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
