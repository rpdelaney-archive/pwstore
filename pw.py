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
import click
import os
import sys
import gnupg
import json


def get_edata(filepath):
    """
    Retrieve data (presumed to be gpg encrypted) from a file and return it raw
    """
    with open(filepath, 'rb') as myfile:
        edata = myfile.read()
    return edata


def decrypt(gpg, edata):
    """
    Take a gpg handler and some data (presumed to be gpg encrypted) and return the decrypted data
    """
    return gpg.decrypt(edata)


def find_gpghome():
    """
    Try to figure out where the gnupg homedir is
    """

    try:
        if os.environ['GNUPGHOME']:
            return os.environ['GNUPGHOME']
    except KeyError:
        pass

    homedir = os.environ['HOME'] + '/.gnupg/'
    tryfile = homedir + 'gpg.conf'
    if os.path.isfile(tryfile):
        return homedir


def find_pwstore():
    try:
        if os.environ['PWSTORE_DIR']:
            return os.environ['PWSTORE_DIR']
    except KeyError:
        pass

    homedir = os.environ['HOME']
    trydir = homedir + '/.pw-store'
    if os.path.isdir(trydir):
        return trydir


def print_friendly(jsondata):
    """ Take a JSON array and return a string fit for printing to screen or file """
    return json.dumps(json.loads(jsondata), sort_keys=False, indent=4)


def get_key(jsondata, key):
    """ Take a JSON array and return the value corresponding to a given key """
    parsed_json = json.loads(str(jsondata))

    return parsed_json[key]


def update_key(jsondata, key, value):
    """ Take a JSON array and update the value of a given key, returning the updated array """
    parsed_json = json.loads(str(jsondata))
    parsed_json[key] = value

    return json.dumps(parsed_json)


@click.command()
@click.argument('record', help)
def main(record):
    gpghome = find_gpghome()
    assert gpghome is not None

    gpg = gnupg.GPG(gnupghome=gpghome, verbose=False)

    pwstore = find_pwstore()
    assert pwstore is not None
    datafile = pwstore + '/' + record + '.gpg'

    edata = get_edata(datafile)
    data = decrypt(gpg, edata)
    print(data)
    print(print_friendly(update_key(data, "url", "foo")))

    return 0


if __name__ == '__main__':
    sys.exit(main())


# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
