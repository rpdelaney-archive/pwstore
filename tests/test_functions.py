#!/usr/bin/env python3

import json
import unittest
import pw
import mock
import tempfile
import dulwich


def get_initialized_dir():
    """ Create and return an initialized git repository in tmpfs """
    git_initialized_dir = tempfile.TemporaryDirectory()
    dulwich.repo.Repo.init(git_initialized_dir.name)
    return git_initialized_dir


def get_empty_dir():
    """ Set up an empty directory (non-initalized git repo) """
    empty_dir = tempfile.TemporaryDirectory()
    return empty_dir


class test_is_initialized(unittest.TestCase):

    def unit_test_nonexistent_dir(self):
        pass

    def unit_test_initialized_dir(self):
        pass

    def unit_test_noninitialized_dir(self):
        pass

    def functional_test_nonexistent_dir(self):
        cwd = 'tests/dir/that/does/not/exist'
        result = pw.is_initialized(cwd)
        self.assertFalse(result)

    def functional_test_initialized_dir(self):
        cwd = get_initialized_dir()
        result = pw.is_initialized(cwd.name)
        self.assertTrue(result)
        cwd.cleanup

    def functional_test_noninitialized_dir(self):
        cwd = get_empty_dir()
        result = pw.is_initialized(cwd.name)
        self.assertFalse(result)
        cwd.cleanup


class test_git_add(unittest.TestCase):

    pass


class test_git_commit(unittest.TestCase):

    def unit_test_commit_is_sent_with_encoded_message(self):
        pass

    @mock.patch('pw.Repo') # Since we import Repo into the module, we need to patch pw.repo
    def unit_test_raise_exception_if_head_doesnt_match_returned_commit(self, repo):
        repo_object = mock.MagicMock() # Repo() returns a repo object, which we mock
        repo_object.commit_id = mock.MagicMock(return_value='foo') # Set the return values
        repo_object.head = mock.MagicMock(return_value='bar')
        repo.return_value = repo_object # Set Repo() to return our mock object
        with self.assertRaises(AssertionError): # Confirm we get an assertion error (Without the with, we'd have to create a lambda and pass it to self.assertRaises as the second arg
            pw.git_commit('a', 'b')

    @mock.patch('pw.Repo')
    def unit_test_repo_called_with_correct_cwd(self, repo):
        repo_object = mock.MagicMock()
        cwd = 'dir/that/does/not/exist'
        repo_object.head = mock.MagicMock(return_value='foo')
        repo_object.do_commit = mock.MagicMock(return_value='foo')
        repo.return_value = repo_object
        pw.git_commit(cwd)
        repo.assert_called_once_with(cwd) # Assert that repo.Repo, i.e. the class, is called with cwd, not repo_object, the instance

    def functional_test_dirty_repo(self):
        pass


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
