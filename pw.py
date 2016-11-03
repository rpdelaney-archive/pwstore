#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Python 3.5.2
#
# © Copyright 2016 Ryan Delaney. All rights reserved.
# This work is distributed WITHOUT ANY WARRANTY whatsoever; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the README file for additional terms and conditions on your use of this
# software.
#
import os
import gnupg

def get_edata(filepath):
    """
    Retrieve data (presumed to be gpg encrypted) from a file and return it raw
    """
    with open(filepath, 'rb') as myfile:
        edata=myfile.read()
    return edata


def decrypt(gpg, edata):
    """
    Take a gpg handler and some data (presumed to be gpg encrypted) and return the decrypted data
    """
    return gpg.decrypt(edata)


def get_gpghome():
    """
    Try to figure out where the gnupg homedir is
    """

    if os.environ['GNUPGHOME']:
        return os.environ['GNUPGHOME']

    homedir = os.environ['HOME'] + '/.gnupg/'
    tryfile = homedir + 'gpg.conf'
    if tryfile.is_file():
        return homedir


def get_pwstore():
    try:
        if os.environ['PWSTORE_DIR']:
            return os.environ['PWSTORE_DIR']
    except KeyError:
        pass

    homedir = os.environ['HOME']
    trydir = homedir + '/.pw-store'
    if trydir.is_dir():
        return trydir


def main():
    gpghome = get_gpghome()
    assert gpghome is not None

    gpg = gnupg.GPG(gnupghome=gpghome, verbose=False)

    pwstore = get_pwstore()
    assert pwstore is not None
    datafile = pwstore + '/xsplit.com.gpg'

    edata = get_edata(datafile)
    data = decrypt(gpg, edata)
    print(data)

if __name__ == '__main__':
    main()


# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
