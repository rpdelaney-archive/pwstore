#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import json
import unittest
import pw
import mock
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


def get_dirty_dir():
    """ Create and return a dirty git repo (file staged) in tmpfs """
    git_file, git_dir = get_unstaged_dir()
    repo = dulwich.repo.Repo(git_dir.name)
    repo.stage(os.path.basename(git_file.name))
    return git_file, git_dir


class test_is_initialized(unittest.TestCase):

    @mock.patch('os.path.isdir')
    def unit_test_os_path_isdir(self, ospath):
        ospath.return_value = False
        cwd = 'dir/that/does/not/exist'
        pw.is_initialized(cwd)
        ospath.assert_called_once_with(cwd)

    @mock.patch('pw.Repo')
    def unit_test_Repo_called(self, repo):
        mydir = get_empty_dir()
        cwd = mydir.name
        pw.is_initialized(cwd)
        mydir.cleanup
        repo.assert_called_once_with(cwd)

    def functional_test_nonexistent_dir(self):
        cwd = 'tests/dir/that/does/not/exist'
        result = pw.is_initialized(cwd)
        self.assertFalse(result)

    def functional_test_initialized_dir(self):
        cwd = get_initialized_dir()
        result = pw.is_initialized(cwd.name)
        cwd.cleanup
        self.assertTrue(result)

    def functional_test_noninitialized_dir(self):
        cwd = get_empty_dir()
        result = pw.is_initialized(cwd.name)
        cwd.cleanup
        self.assertFalse(result)


class test_git_add(unittest.TestCase):

    @mock.patch('pw.Repo')
    def unit_test_repo_stage_called(self, repo):
        repo_object = mock.MagicMock()
        cwd = 'dir/that/does/not/exist'
        myfile = 'dir/that/does/not/exist/file'
        repo.return_value = repo_object
        pw.git_add(cwd, myfile)
        repo_object.stage.assert_called_once_with(os.path.basename(myfile))


class test_git_commit(unittest.TestCase):

    @mock.patch('pw.Repo')
    def unit_test_commit_is_sent_with_encoded_message(self, repo):
        repo_object = mock.MagicMock()
        cwd = 'dir/that/does/not/exist'
        repo_object.head = mock.MagicMock(return_value='foo')
        repo_object.do_commit = mock.MagicMock(return_value='foo')
        repo.return_value = repo_object
        pw.git_commit(cwd, 'mymessage')
        repo_object.do_commit.assert_called_once_with(b'mymessage')

    @mock.patch('pw.Repo')
    def unit_test_raise_exception_if_head_doesnt_match_returned_commit(self, repo):
        repo_object = mock.MagicMock()
        repo_object.commit_id = mock.MagicMock(return_value='foo')
        repo_object.head = mock.MagicMock(return_value='bar')
        repo.return_value = repo_object
        with self.assertRaises(AssertionError):
            pw.git_commit('a', 'b')

    @mock.patch('pw.Repo')
    def unit_test_repo_called_with_correct_cwd(self, repo):
        repo_object = mock.MagicMock()
        cwd = 'dir/that/does/not/exist'
        repo_object.head = mock.MagicMock(return_value='foo')
        repo_object.do_commit = mock.MagicMock(return_value='foo')
        repo.return_value = repo_object
        pw.git_commit(cwd)
        repo.assert_called_once_with(cwd)

    def functional_test_dirty_repo(self):
        git_file, git_dir = get_dirty_dir()
        try:
            pw.git_commit(git_dir.name)
        finally:
            git_dir.cleanup


class test_get_key(unittest.TestCase):

    def test_get_key(self):
        jsonstring = '{"4": "5", "6": "7"}'
        result = pw.get_key(jsonstring, "4")
        self.assertEqual(result, '5')


class test_update_key(unittest.TestCase):

    def test_update_key(self):
        inputjson = '{"4": "5", "6": "7"}'
        targetjson = json.loads('{"4": "5", "6": "8"}')
        result = json.loads(pw.update_key(inputjson, "6", "8"))
        self.assertEqual(result, targetjson)

    def test_update_nonextant_key(self):
        inputjson = '{"4": "5"}'
        targetjson = json.loads('{"4": "5", "6": "8"}')
        result = json.loads(pw.update_key(inputjson, "6", "8"))
        self.assertEqual(result, targetjson)


class test_delete_key(unittest.TestCase):

    def test_delete_key(self):
        inputjson = '{"4": "5", "6": "7"}'
        targetjson = json.loads('{"4": "5"}')
        result = json.loads(pw.delete_key(inputjson, "6"))
        self.assertEqual(result, targetjson)


class test_print_friendly(unittest.TestCase):

    def test_print_friendly(self):
        inputjson = '{"4": "5", "6": "7"}'
        targetjson = '{\n    "4": "5",\n    "6": "7"\n}'
        result = pw.print_friendly(inputjson)
        self.assertEqual(result, targetjson)


# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
