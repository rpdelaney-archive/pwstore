#!/usr/bin/env python3

import unittest

import pw


class test_get_key(unittest.TestCase):

    def test_get_key(self):
        jsonstring = '{"4": "5", "6": "7"}'

        result = pw.get_key(jsonstring, "4")
        self.assertEqual(result, '5')


class test_update_key(unittest.TestCase):

    def test_update_key(self):
        inputjson = '{"4": "5", "6": "7"}'
        targetjson = '{"6": "8", "4": "5"}'
        result = pw.update_key(inputjson, "6", "8")
        self.assertEqual(result, targetjson)


class test_delete_key(unittest.TestCase):

    def test_delete_key(self):
        inputjson = '{"4": "5", "6": "7"}'
        targetjson = '{"4": "5"}'
        result = pw.delete_key(inputjson, "6")
        self.assertEqual(result, targetjson)


class test_print_friendly(unittest.TestCase):

    def test_print_friendly(self):
        inputjson = '{"4": "5", "6": "7"}'
        targetjson = '{\n    "6": "7",\n    "4": "5"\n}'
        result = pw.print_friendly(inputjson)
        self.assertEqual(result, targetjson)


# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
