pwstore
======================

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

Dependencies
~~~~~~~~~~~~

The following non-standard dependencies are required for basic functionality:

::

    pip3 install python-gnupg dulwich appdirs click

There are optional dependencies for some extra features:

To display passwords as QRcodes in the terminal,

::

    pip3 install pyqrcode

To display passwords as QRcodes as images,

::

    pip3 install pyqrcode Pillow pypng

To copy the password to the clipboard,

::

    pip3 install pyperclip

And to type the password at the current cursor position.

::

    pip3 install pyautogui


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
