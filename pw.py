#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Python 3.6
#
# © Copyright 2017 Ryan Delaney. All rights reserved.
# This work is distributed WITHOUT ANY WARRANTY whatsoever; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the README file for additional terms and conditions on your use of this
# software.
#
import appdirs
import click
import os
import logging
import gnupg
import json
import dulwich
from dulwich import porcelain
from dulwich.repo import Repo

# Initialize Logging Module
logger = logging.getLogger(__name__)
if not logger.handlers:
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    logger.setLevel(logging.WARNING)


def is_initialized(cwd):
    """ Verify that a given directory has a git repository in it """
    if not os.path.isdir(cwd):
        return False

    try:
        Repo(cwd)
        return True
    except dulwich.errors.NotGitRepository:
        return False


def git_init(cwd):
    """ Initialize a git repository in a given directory """
    if os.path.isdir(cwd):
        Repo.init(cwd)
    else:
        Repo.init(cwd, mkdir=True)

    logger.warn("WARNING: Initialized a new password store at " + cwd)


def git_add(cwd, filepath):
    """ Stage a file in the pwstore """
    logger.debug('Staging file in pwstore: ' + filepath)
    repo = Repo(cwd)
    repo.stage(os.path.basename(filepath))


def git_commit(cwd, message="Updated given records to password store."):
    """ Commit staged changes to the pwstore """
    logger.debug('Committing staged files to pwstore...')
    repo = Repo(cwd)
    commit_id = repo.do_commit(message.encode())
    assert repo.head() == commit_id


def git_drop(cwd, target):
    """ Remove a tracked file from a repository & delete from disk """
    logger.warn("WARNING: Dropping record " + target + " from repository " + cwd)
    porcelain.rm(cwd, [target])
    os.unlink(os.path.abspath(os.path.join(cwd, target)))
    git_commit(cwd, "Dropped record " + target + " from password store.")


def save_edata(edata, filepath):
    """ Takes data (presumed to be gpg encrypted) and saves it to a file """
    with open(filepath, 'w+') as myfile:
        logger.debug('Writing encrypted data to file ' + filepath)
        myfile.write(str(edata))


def get_edata(filepath):
    """ Retrieve data (presumed to be gpg encrypted) from a file and return it raw """
    with open(filepath, 'rb') as myfile:
        logger.debug('Reading encrypted data from file ' + filepath)
        edata = myfile.read()
    return edata


def decrypt(gpg, edata):
    """ Take a gpg handler and some data (presumed to be gpg encrypted) and return the decrypted data """
    return gpg.decrypt(edata)


def encrypt(gpg, data):
    """ Take a gpg handler and some data (presumed to be plain text) and return encrypted data """
    recipient = find_recipient()
    edata = gpg.encrypt(data, recipient)
    return edata


def get_data(gpg, filepath):
    """ Retrieve data (presumed to be gpg encrypted) from a file and return it as a decrypted string """
    edata = get_edata(filepath)
    data = decrypt(gpg, edata)
    return str(data)


def find_recipient():
    """ Try to figure out who the gpg recipient should be for encrypted data """
    try:
        rkey = os.environ['PWSTORE_KEY']
        if rkey:
            logger.debug("Recipient key is: " + rkey)
            return rkey
    except KeyError:
        raise RuntimeError("Failed to encrypt data. PWSTORE_KEY is not set.")


def find_gpghome():
    """ Try to figure out where the gnupg homedir is """
    try:
        gdir = os.environ['GNUPGHOME']
        if gdir:
            logger.debug("GNUPGHOME is: " + gdir)
            return gdir
    except KeyError:
        pass

    homedir = os.path.join(os.environ['HOME'], '/.gnupg/')
    tryfile = os.path.join(homedir, 'gpg.conf')
    if os.path.isfile(tryfile):
        return homedir


def find_pwstore():
    """ Try to find out where the password store directory is """
    trydir = os.environ.get('PWSTORE_DIR')
    if trydir is not None and os.path.isdir(trydir):
        return trydir

    return appdirs.user_data_dir('pwstore')


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
    try:
        assert gpghome is not None
        gpg = gnupg.GPG(gnupghome=gpghome, verbose=False, use_agent=True)
    except AssertionError:
        logger.critical("FATAL: GNUPGHOME could not be found.")

    pwstore = find_pwstore()
    assert pwstore is not None

    datafile = os.path.join(pwstore, record + '.gpg')

    # Define the context object to be passed
    ctx.obj = {
        'record': record,
        'gpg': gpg,
        'pwstore': pwstore,
        'datafile': datafile
    }

    # Check that the pwstore has been initialized.
    if not is_initialized(pwstore):
        git_init(pwstore)

    return 0


@main.command()
@click.pass_context
def list(ctx):
    """ List the keys in a record """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    mydict = json.loads(str(data))
    for item in mydict.keys():
        print(item)


@main.command()
@click.pass_context
def add(ctx):
    """ Create a new record """
    data = '{\n}'
    if os.path.exists(ctx.obj['datafile']):
        logger.critical("Record title already exists. Nothing was done.")
    else:
        edata = encrypt(ctx.obj['gpg'], data)
        save_edata(edata, ctx.obj['datafile'])
        git_add(find_pwstore(), ctx.obj['datafile'])
        git_commit(ctx.obj['pwstore'], "Created empty record " + os.path.basename(ctx.obj['datafile']))


@main.command()
@click.argument('key')
@click.pass_context
def delete(ctx, key):
    """ Delete KEY from a record """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    newdata = delete_key(data, key)
    save_edata(encrypt(ctx.obj['gpg'], newdata), ctx.obj['datafile'])
    git_add(find_pwstore(), ctx.obj['datafile'])
    git_commit(ctx.obj['pwstore'])


@main.command()
@click.argument('key')
@click.pass_context
def get(ctx, key):
    """ Retrieve a KEY value from a record """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    print(get_key(data, key))


@main.command()
@click.argument('key')
@click.pass_context
def qrcode(ctx, key):
    """ Display a KEY value as a qrcode """
    try:
        import pyqrcode
    except ImportError:
        raise RuntimeError("Required library not found: qrcode")

    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    value = get_key(data, key)
    code = pyqrcode.create(value)
    print(code.terminal(quiet_zone=1))


@main.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def update(ctx, key, value):
    """ Update a record's KEY with VALUE """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    newdata = update_key(data, key, value)
    save_edata(encrypt(ctx.obj['gpg'], newdata), ctx.obj['datafile'])
    git_add(find_pwstore(), ctx.obj['datafile'])
    git_commit(ctx.obj['pwstore'])


@main.command()
@click.pass_context
def select(ctx):
    """ Decrypt a record and print it raw """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    print_friendly(data)


@main.command()
@click.pass_context
def drop(ctx):
    """ Delete an entire record from the disk """
    if os.path.exists(ctx.obj['datafile']):
        cwd = ctx.obj['pwstore']
        target = os.path.basename(ctx.obj['datafile'])
        git_drop(cwd, target)
    else:
        logger.critical("Record title does not exist. Nothing was done.")


@main.command()
@click.argument('alias')
@click.pass_context
def alias(ctx, alias):
    """ Create a symlink named ALIAS """
    source = ctx.obj['datafile']
    target = os.path.join(ctx.obj['pwstore'], alias + '.gpg')
    os.symlink(source, target)
    git_add(ctx.obj['pwstore'], target)
    git_commit(ctx.obj['pwstore'])


@main.command()
@click.argument('key')
@click.pass_context
def copy(ctx, key):
    """ Copy a KEY value to the system clipboard """
    try:
        import pyperclip
        data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
        value = get_key(data, key)
        pyperclip.copy(value)
    except ModuleNotFoundError:
        raise RuntimeError("Required library not found: pyperclip")


@main.command()
@click.argument('key')
@click.pass_context
def type(ctx, key):
    """ Type a KEY value at the cursor position """
    try:
        import pyautogui
        data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
        value = get_key(data, key)
        pyautogui.typewrite(value)
    except ModuleNotFoundError:
        raise RuntimeError("Required library not found: pyautogui")


if __name__ == '__main__':
    main()


# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
