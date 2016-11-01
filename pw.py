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


# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
