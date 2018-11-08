#!/usr/bin/env python3
# Python 3.6
#
# © Copyright 2017-2018 Ryan Delaney. All rights reserved.
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
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)


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

    logger.warn("Initialized a new password store at {}".format(cwd))


def git_add(cwd, filepath):
    """ Stage a file in the pwstore """
    logger.debug("Staging file in pwstore: {}".format(filepath))
    repo = Repo(cwd)
    repo.stage(os.path.basename(filepath))


def git_commit(cwd, message="Updated given records to password store."):
    """ Commit staged changes to the pwstore """
    logger.debug("Committing staged files to pwstore...")
    repo = Repo(cwd)
    commit_id = repo.do_commit(message.encode())
    assert repo.head() == commit_id


def git_drop(cwd, target):
    """ Remove a tracked file from a repository & delete from disk """
    if os.path.exists(target):
        target = os.path.basename(target)
        logger.warn("Dropping record {} from repository {}".format(
            target, cwd))
        porcelain.rm(cwd, [target])
        os.unlink(os.path.abspath(os.path.join(cwd, target)))
        git_commit(cwd, "Dropped record {} from password store.".format(
            target))
    else:
        logger.critical("Record title does not exist. Nothing was done.")


def symlink(cwd, source, target):
    """ Create a symlink (alias) from source to target in the pwstore """
    os.symlink(source, target)
    git_add(cwd, target)
    git_commit(cwd)


def save_edata(edata, filepath):
    """ Takes data (presumed to be gpg encrypted) and saves it to a file """
    with open(filepath, 'w+') as myfile:
        logger.debug("Writing encrypted data to file {}".format(filepath))
        myfile.write(str(edata))


def get_edata(filepath):
    """
    Retrieve data (presumed to be gpg encrypted) from a file and return it raw
    """
    with open(filepath, 'rb') as myfile:
        logger.debug("Reading encrypted data from file {}".format(filepath))
        edata = myfile.read()
    return edata


def decrypt(gpg, edata):
    """
    Take a gpg handler and some data (presumed to be gpg encrypted) and return
    the decrypted data
    """
    data = gpg.decrypt(edata)
    try:
        assert data.ok
    except AssertionError:
        logger.critical("GPG decryption failed. Status was: {}".format(
            data.status))
        raise
    return data


def encrypt(gpg, data):
    """
    Take a gpg handler and some data (presumed to be plain text) and return
    encrypted data
    """
    recipient = find_recipient()
    edata = gpg.encrypt(data, recipient)
    try:
        assert edata.ok
    except AssertionError:
        logger.critical("GPG encryption failed. Status was: {}".format(
            edata.status))
        raise
    return edata


def get_data(gpg, filepath):
    """
    Retrieve data (presumed to be gpg encrypted) from a file and return it as a
    decrypted string
    """
    edata = get_edata(filepath)
    data = decrypt(gpg, edata)
    return str(data)


def find_recipient():
    """
    Try to figure out who the gpg recipient should be for encrypted data
    """
    try:
        rkey = os.environ['PWSTORE_KEY']
        if rkey:
            logger.debug("Recipient key is: {}".format(rkey))
            return rkey
    except KeyError:
        raise RuntimeError("Failed to encrypt data. PWSTORE_KEY is not set.")


def find_gpghome():
    """ Try to figure out where the gnupg homedir is """
    try:
        gdir = os.environ['GNUPGHOME']
        if gdir:
            logger.debug("GNUPGHOME is: {}".format(gdir))
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


def parse_json(data):
    """ Take an object (presumed to be json data) and return a dict """
    return json.loads(str(data))


def get_key(jsondata, key):
    """ Take a JSON array and return the value corresponding to a given key """
    parsed_json = parse_json(jsondata)
    return parsed_json[key]


def update_key(jsondata, key, value):
    """
    Take a JSON array and update the value of a given key, returning the
    updated array
    """
    parsed_json = parse_json(jsondata)
    parsed_json[key] = value
    return json.dumps(parsed_json)


def delete_key(jsondata, key):
    """ Take a JSON array and remove a key, returning the updated array """
    parsed_json = parse_json(jsondata)
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
        logger.critical("GNUPGHOME could not be found.")
        raise

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
    mydict = parse_json(data)
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
        git_add(ctx.obj['pwstore'], ctx.obj['datafile'])
        git_commit(ctx.obj['pwstore'], "Created empty record {}".format(
            os.path.basename(ctx.obj['datafile'])))


@main.command()
@click.argument('key')
@click.pass_context
def delete(ctx, key):
    """ Delete KEY from a record """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    newdata = delete_key(data, key)
    save_edata(encrypt(ctx.obj['gpg'], newdata), ctx.obj['datafile'])
    git_add(ctx.obj['pwstore'], ctx.obj['datafile'])
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
@click.argument('value')
@click.pass_context
def update(ctx, key, value):
    """ Update a record's KEY with VALUE """
    data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
    newdata = update_key(data, key, value)
    save_edata(encrypt(ctx.obj['gpg'], newdata), ctx.obj['datafile'])
    git_add(ctx.obj['pwstore'], ctx.obj['datafile'])
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
    git_drop(ctx.obj['pwstore'], ctx.obj['datafile'])


@main.command()
@click.argument('alias')
@click.pass_context
def alias(ctx, alias):
    """ Create a symlink named ALIAS """
    source = ctx.obj['datafile']
    target = os.path.join(ctx.obj['pwstore'], alias + '.gpg')
    cwd = ctx.obj['pwstore']
    symlink(cwd, source, target)


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
    except ImportError:
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
    except ImportError:
        raise RuntimeError("Required library not found: pyautogui")


@main.command()
@click.pass_context
def search(ctx):
    """ Find a record in the pwstore by title """
    result = []
    for f in os.listdir(ctx.obj['pwstore']):
        if os.path.isfile(os.path.join(ctx.obj['pwstore'], f)):
            if ctx.obj['record'].upper() in f.upper():
                result.append(f.replace('.gpg', ''))
    print('\n'.join(result))


@main.command()
@click.argument('key')
@click.pass_context
def qrcode(ctx, key):
    """ Display a KEY value as a qrcode """
    try:
        import pyqrcode
        data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
        value = get_key(data, key)
        code = pyqrcode.create(value)
        print(code.terminal(quiet_zone=1))
    except ImportError:
        raise RuntimeError("Required library not found: pyqrcode")


@main.command()
@click.argument('key')
@click.pass_context
def qrcodei(ctx, key):
    """ Display a KEY value as a qrcode in a png """
    try:
        import pyqrcode
        import tempfile
        from PIL import Image
        data = get_data(ctx.obj['gpg'], ctx.obj['datafile'])
        value = get_key(data, key)
        code = pyqrcode.create(value)
        with tempfile.NamedTemporaryFile(
                prefix='pwstore-', suffix='.png') as f:
            code.png(f.name, scale=10, quiet_zone=2)
            img = Image.open(f.name)
            img.show()
    except ImportError:
        raise RuntimeError("Required library not found: pyqrcode")


if __name__ == '__main__':
    main()


# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4
