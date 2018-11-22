Using the web module
====================

Filabel can be used as an automatic web application. It uses the `Flask <http://flask.pocoo.org/>`_ framewrork.

Additional preparations
-----------------------
If you've installed filabel and you've done all the preparations described in :ref:`prep-ref`, you need to prepare a little bit more. 

Environment variables
^^^^^^^^^^^^^^^^^^^^^
First of all, you need to export an environment variable called ``FILABEL_CONFIG`` with the names of the configuration files you have prepared:

.. code-block:: none

   $ export FILABEL_CONFIG=cred.cfg:label.cfg

Notice that the filenames are separated by ':'. The order of the names does not matter.

Next, you need to export another environment variable. This time it is for the purposes of Flask. The variable must be called ``FLASK_APP``:

.. code-block:: none

   $ export FLASK_APP=filabel


Running the app
^^^^^^^^^^^^^^^
When this is done, you can run the web module by running:

.. code-block:: none

   $ flask run

The application should start and print its address on the standard output. It you open the address in your browser, the homepage is shown. It displays the labeling rules and the name of the repository owner.

However, the setup is not over yet.


.. _webhook-ref:

GitHub Webhook
^^^^^^^^^^^^^^
In order for filabel to work, you must set a `webhook <https://developer.github.com/webhooks/>`_ in your GitHub repository. Webhook will basically tell GitHub to notify your application whenever a certain even occurs (you can choose which events you want to be notified about, filabel can only work with ping and pull request).

In order to set a webhook, go to your repository GitHub page, click ``Settings`` and then ``Webhooks``. Click ``Add a webhook``. Type the address of the running application into ``Payload URL`` field, choose JSON as ``Context type`` and then choose a secret.

The secret is a private information that will be used to generate a ``X-Hub-Signature`` that will be a part of every message the app gets from GitHub. Please include the secret into the credentials coniguration file, so that the signatures can be checked. **You shouldn't make the secret public** as it prevents the messages from GitHub from being altered.

After setting the webhook and adding the secret to the configuration file, the application should work now. It print all the error messages on the standard output, so it might be a good idea to redirect it to some kind of log file if you are able to.

