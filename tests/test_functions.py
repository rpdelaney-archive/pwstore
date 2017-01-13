#!/usr/bin/env python3

import json
import unittest
import pw
from unittest.mock import patch


class test_git_add(unittest.TestCase):

    pass

class test_git_commit(unittest.TestCase):

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
