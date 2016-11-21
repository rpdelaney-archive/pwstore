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

# vim: ft=python expandtab smarttab shiftwidth=4 softtabstop=4 fileencoding=UTF-8:
