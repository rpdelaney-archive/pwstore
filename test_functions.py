#!/usr/bin/env python3
# pylint: disable=no-self-use, missing-docstring, too-few-public-methods

import os
import shutil
import json
import pytest
import pwstore
import tempfile
import dulwich


def get_empty_dir():
    """ Set up an empty directory (non-initalized git repo) """
    empty_dir = tempfile.TemporaryDirectory()
    return empty_dir


def get_initialized_dir():
    """ Create and return an initialized git repository in tmpfs """
    git_initialized_dir = get_empty_dir()
    dulwich.repo.Repo.init(git_initialized_dir.name)
    return git_initialized_dir


def get_unstaged_dir():
    """ Create and return a dirty git repo (file unstaged) in tmpfs """
    git_dir = get_initialized_dir()
    git_file = tempfile.NamedTemporaryFile(dir=git_dir.name, delete=False)
    return git_file, git_dir


def get_staged_dir():
    """ Create and return a dirty git repo (file staged) in tmpfs """
    git_file, git_dir = get_unstaged_dir()
    repo = dulwich.repo.Repo(git_dir.name)
    repo.stage(os.path.basename(git_file.name))
    return git_file, git_dir


def get_clean_dir():
    """
    Create and return a clean git repo (file tracked, unstaged) in tmpfs
    """
    git_file, git_dir = get_staged_dir()
    repo = dulwich.repo.Repo(git_dir.name)
    commit_id = repo.do_commit(b'test')
    assert repo.head() == commit_id
    return git_file, git_dir


class test_is_initialized():

    def unit_test_os_path_isdir(self, mocker):
        mocker.patch('os.path.isdir', return_value=False)
        cwd = 'dir/that/does/not/exist'
        pwstore.is_initialized(cwd)
        os.path.isdir.assert_called_once_with(cwd)

    def unit_test_Repo_called(self, mocker):
        mocker.patch('pwstore.Repo')
        mydir = get_empty_dir()
        cwd = mydir.name
        try:
            pwstore.is_initialized(cwd)
        finally:
            mydir.cleanup
        pwstore.Repo.assert_called_once_with(cwd)

    def functional_test_nonexistent_dir(self):
        cwd = 'tests/dir/that/does/not/exist'
        result = pwstore.is_initialized(cwd)
        assert result is False

    def functional_test_initialized_dir(self):
        cwd = get_initialized_dir()
        try:
            result = pwstore.is_initialized(cwd.name)
        finally:
            cwd.cleanup
        assert result is True

    def functional_test_noninitialized_dir(self):
        cwd = get_empty_dir()
        try:
            result = pwstore.is_initialized(cwd.name)
        finally:
            cwd.cleanup
        assert result is False


class test_git_init():

    def unit_test_repo_init_called(self, mocker):
        mocker.patch('pwstore.Repo')
        cwd = 'dir/that/does/not/exist'
        pwstore.git_init(cwd)
        pwstore.Repo.init.assert_called_once_with(cwd, mkdir=True)

    def functional_test_nonexisting_dir(self):
        cwd = 'dirthatdoesnotexist/'
        try:
            pwstore.git_init(cwd)
            dulwich.repo.Repo(cwd)
        finally:
            shutil.rmtree(cwd)

    def functional_test_existing_dir(self):
        cwd = get_empty_dir()
        try:
            pwstore.git_init(cwd.name)
            dulwich.repo.Repo(cwd.name)
        finally:
            cwd.cleanup


class test_git_add():

    def unit_test_repo_stage_called(self, mocker):
        mocker.patch('pwstore.Repo')
        repo_object = mocker.MagicMock()
        cwd = 'dir/that/does/not/exist'
        myfile = 'dir/that/does/not/exist/file'
        pwstore.Repo.return_value = repo_object
        pwstore.git_add(cwd, myfile)
        repo_object.stage.assert_called_once_with(os.path.basename(myfile))

    def functional_test_git_add(self):
        git_file, git_dir = get_unstaged_dir()
        repo = dulwich.repo.Repo(git_dir.name)
        index = repo.open_index()
        try:
            assert list(index) == []
            pwstore.git_add(git_dir.name, git_file.name)
            index = repo.open_index()
            assert list(index) == [os.path.basename(git_file.name).encode()]
        finally:
            git_dir.cleanup


class test_git_commit():

    def unit_test_commit_is_sent_with_encoded_message(self, mocker):
        mocker.patch('pwstore.Repo')
        repo_object = mocker.MagicMock()
        cwd = 'dir/that/does/not/exist'
        repo_object.head = mocker.MagicMock(return_value='foo')
        repo_object.do_commit = mocker.MagicMock(return_value='foo')
        pwstore.Repo.return_value = repo_object
        pwstore.git_commit(cwd, 'mymessage')
        repo_object.do_commit.assert_called_once_with(b'mymessage')

    def unit_test_raise_exception_if_head_doesnt_match_returned_commit(
            self, mocker):
        mocker.patch('pwstore.Repo')
        repo_object = mocker.MagicMock()
        repo_object.commit_id = mocker.MagicMock(return_value='foo')
        repo_object.head = mocker.MagicMock(return_value='bar')
        pwstore.Repo.return_value = repo_object
        with pytest.raises(RuntimeError):
            pwstore.git_commit('a', 'b')

    def unit_test_repo_called_with_correct_cwd(self, mocker):
        mocker.patch('pwstore.Repo')
        repo_object = mocker.MagicMock()
        cwd = 'dir/that/does/not/exist'
        repo_object.head = mocker.MagicMock(return_value='foo')
        repo_object.do_commit = mocker.MagicMock(return_value='foo')
        pwstore.Repo.return_value = repo_object
        pwstore.git_commit(cwd)
        pwstore.Repo.assert_called_once_with(cwd)

    def functional_test_dirty_repo(self):
        git_file, git_dir = get_staged_dir()
        try:
            pwstore.git_commit(git_dir.name)
        finally:
            git_dir.cleanup


class test_git_drop():

    def unit_test_exists_called_on_target(self, mocker):
        mocker.patch('os.path.exists')
        mocker.patch('pwstore.porcelain.rm')
        mocker.patch('os.unlink')
        mocker.patch('os.path.basename')
        mocker.patch('pwstore.git_commit')
        cwd = '/dir/that/does/not/exist'
        target = '/dir/that/does/not/exist/file'
        os.path.basename.return_value = 'file'
        pwstore.git_drop(cwd, target)
        os.path.exists.assert_called_once_with(target)

    def unit_test_basename_called_on_target(self, mocker):
        mocker.patch('os.path.exists')
        mocker.patch('pwstore.porcelain.rm')
        mocker.patch('os.unlink')
        mocker.patch('os.path.basename')
        mocker.patch('pwstore.git_commit')
        cwd = '/dir/that/does/not/exist'
        target = '/dir/that/does/not/exist/file'
        os.path.basename.return_value = 'file'
        pwstore.git_drop(cwd, target)
        os.path.basename.assert_any_call(target)

    def unit_test_porcelain_rm_called_on_target(self, mocker):
        mocker.patch('os.path.exists')
        mocker.patch('pwstore.porcelain.rm')
        mocker.patch('os.unlink')
        mocker.patch('os.path.basename')
        mocker.patch('pwstore.git_commit')
        cwd = '/dir/that/does/not/exist'
        target = '/dir/that/does/not/exist/file'
        os.path.basename.return_value = 'file'
        pwstore.git_drop(cwd, target)
        pwstore.porcelain.rm.assert_called_once_with(cwd, [target])

    def unit_test_git_commit_called(self, mocker):
        mocker.patch('os.path.exists')
        mocker.patch('pwstore.porcelain.rm')
        mocker.patch('os.unlink')
        mocker.patch('os.path.basename')
        mocker.patch('pwstore.git_commit')
        cwd = '/dir/that/does/not/exist'
        target = '/dir/that/does/not/exist/file'
        os.path.basename.return_value = 'file'
        pwstore.git_drop(cwd, target)
        pwstore.git_commit.assert_called_once_with(
            cwd, "Dropped record {} from password store.".format(
                os.path.basename.return_value))

    def functional_test_file_removed(self):
        git_file, git_dir = get_clean_dir()
        pwstore.git_drop(git_dir.name, git_file.name)
        try:
            assert not os.path.exists(git_file.name)
        finally:
            git_dir.cleanup


class test_symlink():

    def unit_test_os_symlink_called(self, mocker):
        mocker.patch('pwstore.git_commit')
        mocker.patch('pwstore.git_add')
        mocker.patch('os.symlink')
        cwd = '/dir/that/does/not/exist/'
        source = '/dir/that/does/not/exist/source'
        target = '/dir/that/does/not/exist/target'
        pwstore.symlink(cwd, source, target)
        os.symlink.assert_called_once_with(source, target)

    def unit_test_git_add_called(self, mocker):
        mocker.patch('pwstore.git_commit')
        mocker.patch('pwstore.git_add')
        mocker.patch('os.symlink')
        cwd = '/dir/that/does/not/exist/'
        source = '/dir/that/does/not/exist/source'
        target = '/dir/that/does/not/exist/target'
        pwstore.symlink(cwd, source, target)
        pwstore.git_add.assert_called_once_with(cwd, target)

    def unit_test_git_commit_called(self, mocker):
        mocker.patch('pwstore.git_commit')
        mocker.patch('pwstore.git_add')
        mocker.patch('os.symlink')
        cwd = '/dir/that/does/not/exist/'
        source = '/dir/that/does/not/exist/source'
        target = '/dir/that/does/not/exist/target'
        pwstore.symlink(cwd, source, target)
        pwstore.git_commit.assert_called_once_with(cwd)

    def functional_test_symlink_created(self):
        git_file, git_dir = get_clean_dir()
        cwd = git_dir.name
        source = git_file.name
        target = source + ".foo"
        try:
            pwstore.symlink(cwd, source, target)
            assert os.path.islink(target)
        finally:
            git_dir.cleanup


class test_parse_json():

    def unit_test_json_loads_called(self, mocker):
        mocker.patch('json.loads')
        jsonstring = '{"4": "5", "6": "7"}'
        pwstore.parse_json(jsonstring)
        json.loads.assert_called_once_with(jsonstring)

    def functional_test_returns_dict(self):
        jsonstring = '{"4": "5", "6": "7"}'
        result = pwstore.parse_json(jsonstring)
        assert isinstance(result, dict)


class test_get_key():

    def functional_test_get_key(self):
        jsonstring = '{"4": "5", "6": "7"}'
        result = pwstore.get_key(jsonstring, "4")
        assert result == '5'


class test_update_key():

    def functional_test_update_key(self):
        inputjson = '{"4": "5", "6": "7"}'
        targetjson = json.loads('{"4": "5", "6": "8"}')
        result = json.loads(pwstore.update_key(inputjson, "6", "8"))
        assert result == targetjson

    def functional_test_update_nonextant_key(self):
        inputjson = '{"4": "5"}'
        targetjson = json.loads('{"4": "5", "6": "8"}')
        result = json.loads(pwstore.update_key(inputjson, "6", "8"))
        assert result == targetjson


class test_delete_key():

    def functional_test_delete_key(self):
        inputjson = '{"4": "5", "6": "7"}'
        targetjson = json.loads('{"4": "5"}')
        result = json.loads(pwstore.delete_key(inputjson, "6"))
        assert result == targetjson


class test_print_friendly():

    def functional_test_print_friendly(self):
        inputjson = '{"4": "5", "6": "7"}'
        targetjson = '{\n    "4": "5",\n    "6": "7"\n}'
        result = pwstore.print_friendly(inputjson)
        assert result == targetjson


# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4
