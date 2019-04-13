pwstore
======================
.. |img-pypi| https://img.shields.io/pypi/format/pwstore.svg?color=blue&label=pwstore&logo=pwstore&style=for-the-badge
.. |url-pypi| https://pypi.org/project/pwstore/
.. |badge-pypi| image:: |img-pypi|  :alt: PyPI - Format :target: |url-pypi|

.. |img-circleci| https://img.shields.io/circleci/project/github/rpdelaney/pwstore/master.svg?style=for-the-badge
.. |url-circleci| https://circleci.com/gh/rpdelaney/pwstore
.. |badge-circleci| image:: |img-circleci|  :alt: CircleCI - Status :target: |url-circleci|

|badge-pypi| |badge-circleci|

A cli password manager in python. Inspired by
password-store[`1 <https://www.passwordstore.org/>`__] by Jason A.
Donenfeld.

Usage
-----

::

    Usage: pwstore [OPTIONS] RECORD COMMAND [ARGS]...

    Options:
    -?, -h, --help  Show this message and exit.

    Commands:
    add      Create a new record
    alias    Create a symlink named ALIAS
    copy     Copy a KEY value to the system clipboard
    delete   Delete KEY from a record
    drop     Delete an entire record from the disk
    get      Retrieve a KEY value from a record
    list     List the keys in a record
    qrcode   Display a KEY value as a qrcode
    qrcodei  Display a KEY value as a qrcode in a png
    select   Decrypt a record and print it raw
    type     Type a KEY value at the cursor position
    update   Update a record's KEY with VALUE

Installation
~~~~~~~~~~~~

::

    pip3 install pwstore


If you want to clone and run it locally:

::

    git clone git@github.com:rpdelaney/pwstore.git && pip3 install ./pwstore

GPG
~~~

Like password-store, pwstore uses GPG encryption to store data securely.
For now, you must set your recipient key in the environment:

::

    export PWSTORE_KEY='0xA96895ACB7F4970C'

Examples
~~~~~~~~

Create a new record
^^^^^^^^^^^^^^^^^^^

::

    pwstore github.com add

Create an alias
^^^^^^^^^^^^^^^

::

    pwstore github.com alias github

Add a password
^^^^^^^^^^^^^^

::

    pwstore github update password "$(apg -n1)"

Add some metadata
^^^^^^^^^^^^^^^^^

::

    pwstore github update login_url "http://github.com"
    pwstore github update username rpdelaney

Why use pw?
-----------

In most cases, you should use password-store. Overall, it is much more
mature and feature-rich.

The main difference is that pwstore stores data in a json format, enabling
you to store additional metadata such as username, login page URL, etc:

::

    pwstore github.com update username rpdelaney
