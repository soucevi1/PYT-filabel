Using the CLI module
====================

You can run filabel from the command line in order to label the pull requests of the given repositories.


.. code-block:: none

   $ python -m filabel [OPTIONS] [REPOSLUGS]

Options
-------
You can pass several arguments to filabel. To find out which, use ``--help``.

* ``-s``, ``--state``: State of the pull requests that will be labeled. Can be ``open`` (default), ``closed`` or ``all``.
* ``-d``, ``--delete-old``: Flag indicating that old labels that were already on the pull request and should not be used now will be deleted (default).
* ``-D``, ``--no-delete-old``: Same as above, the old usuned labels will be kept.
* ``-b BRANCH``, ``--base BRANCH``: Base branch where the pull request will be labeled (edfault: master).
* ``-a FILENAME``, ``--config-auth FILENAME``: Name of the configuration file that contains the credentials (GitHub token and secret).
* ``-l FILENAME``, ``--config-labels FILENAME``: Name of the configuration file containing labeling rules.
* ``--help``: Show help.

Reposlugs
---------
The ``REPOSLUGS`` argument is a list of reposiroty names. All should look like ``repo-owner/repo-name``.

Output
------
The output is produced on the ``stdout``. You might want to turn on colored output in your terminal settings. The output consists of several parts as you can see in the example below:

.. code-block:: none

   REPO myaccount/myrepo - OK
     PR https://github.com/myaccount/myrepo/testpull/pull/4 - OK
       + frontend
     PR https://github.com/myaccount/myrepo/testpull/pull/1 - OK
       - backend
       + docs
       = frontend
   REPO myaccount/myfakerepo - FAIL

The keyword ``REPO`` shows which repository is currently being processed. If a green ``OK`` is displayed next to its name, it means that the program correctly connected and authorized to the repository (first case in the example, repository ``myaccount/myrepo`` is fine). If a red ``FAIL`` is displayed next to it, it means that there was an error in the connection (second repository in the example -- ``myaccount/myfakerepo`` probably does not exist or the token owner does not have requires privileges.).

The keyword ``PR`` means 'pull request'. Next to it, the URL of the currently processed pull request is shown, together with the success indication, just like it is with the repositories. Underneath you can see that there is a sign (``+``, ``-`` or ``=``). The sign means that the label displayed next to it was either added (``+``), removed (``-``) or kept (``=``).