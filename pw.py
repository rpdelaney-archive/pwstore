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
import appdirs
import click
import os
import sys
import logging
import subprocess
import gnupg
import json

# Initialize Logging Module
logger = logging.getLogger(__name__)
if not logger.handlers:
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    logger.setLevel(logging.WARNING)


def git_add(filepath):
    """ Stage a file in the pwstore """
    cmd = ['git', 'add', filepath]
    cwd = find_pwstore()
    subprocess.check_call(cmd, cwd=cwd)


def git_commit():
    """ Commit staged changes to the pwstore """
    message = "Updated given records to pwstore."
    cmd = ['git', 'commit', '-m', message]
    cwd = find_pwstore()
    subprocess.check_call(cmd, cwd=cwd)


def save_edata(edata, filepath):
    """
    Takes data (presumed to be gpg encrypted) and saves it to a file
    """
    with open(filepath, 'w+') as myfile:
        myfile.write(str(edata))


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


def encrypt(gpg, data):
    """
    Take a gpg handler and some data (presumed to be plain text) and return encrypted data
    """
    recipient = find_recipient()
    edata = gpg.encrypt(data, recipient)
    return edata


def get_data(gpg, filepath):
    """
    Retrieve data (presumed to be gpg encrypted) from a file and return it as a decrypted string
    """
    edata = get_edata(filepath)
    data = decrypt(gpg, edata)
    return str(data)


def find_recipient():
    """
    Try to figure out who the gpg recipient should be for encrypted data
    """
    try:
        if os.environ['PWSTORE_KEY']:
            return os.environ['PWSTORE_KEY']
    except KeyError:
        logger.critical("Failed to encrypt data. PWSTORE_KEY is not set.")
        sys.exit(1)


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
    """
    Try to find out where the password store directory is
    """
    try:
        if os.path.isdir(os.environ['PWSTORE_DIR']):
            return os.environ['PWSTORE_DIR']
    except KeyError:
        pass

    trydir = appdirs.user_data_dir('pwstore')
    if os.path.isdir(trydir):
        return trydir


def print_friendly(jsondata):
    """ Take a JSON array and pretty-print a string representation """
    pretty_string = json.dumps(json.loads(jsondata), sort_keys=True, indent=4)
    print(pretty_string)
    return pretty_string


def get_key(jsondata, key):
    """ Take a JSON array and return the value corresponding to a given key """
    parsed_json = json.loads(str(jsondata))
    return parsed_json[key]


def update_key(jsondata, key, value):
    """ Take a JSON array and update the value of a given key, returning the updated array """
    parsed_json = json.loads(str(jsondata))
    parsed_json[key] = value
    return json.dumps(parsed_json)


def delete_key(jsondata, key):
    """ Take a JSON array and remove a key, returning the updated array """
    parsed_json = json.loads(str(jsondata))
    parsed_json.pop(key)
    return json.dumps(parsed_json)


CONTEXT_SETTINGS = {'help_option_names': ['-?', '-h', '--help']}
@click.group(context_settings=CONTEXT_SETTINGS)
@click.argument('record')
@click.pass_context
def main(ctx, record):
    gpghome = find_gpghome()
    assert gpghome is not None
    gpg = gnupg.GPG(gnupghome=gpghome, verbose=False, use_agent=True)
    pwstore = find_pwstore()
    assert pwstore is not None

    datafile = pwstore + '/' + record + '.gpg'

    # Define the context object to be passed
    ctx.obj = {
        'record': record,
        'gpg': gpg,
        'pwstore': pwstore,
        'datafile': datafile
    }
    return 0


@main.command()
@click.pass_context
def list(ctx):
    """
    List the keys in a record
    """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    mydict = json.loads(str(data))
    for item in mydict.keys():
        print(item)


@main.command()
@click.pass_context
def add(ctx):
    """
    Create a new record
    """
    data = '{\n}'
    edata = encrypt(ctx.obj['gpg'], data)
    save_edata(edata, ctx.obj['datafile'])


@main.command()
@click.argument('key')
@click.pass_context
def delete(ctx, key):
    """
    Delete KEY from a record
    """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    print_friendly(delete_key(data, key))


@main.command()
@click.argument('key')
@click.pass_context
def get(ctx, key):
    """
    Retrieve a KEY value from a record
    """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    print(get_key(data, key))


@main.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def update(ctx, key, value):
    """
    Update a record's KEY with VALUE
    """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    print_friendly(update_key(data, key, value))


@main.command()
@click.pass_context
def select(ctx):
    """
    Decrypt a record and print it raw
    """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    print_friendly(data)


@main.command()
@click.pass_context
def drop(ctx):
    """
    Delete an entire record from the disk
    """
    pass


if __name__ == '__main__':
    sys.exit(main())


# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
