#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Running the tests:
# $ python3 -m unittest discover --start-directory ./tests/
# Checking the coverage of the tests:
# $ coverage run --include=./*.py --omit=tests/* -m unittest discover && \
#   rm -rf html_dev/coverage && coverage html --directory=html_dev/coverage \
#   --title="Code test coverage for billingflatfile"

import unittest
import sys
import os
import io
import contextlib
import logging

sys.path.append('.')
target = __import__("billingflatfile")


class TestParseArgs(unittest.TestCase):
    def test_parse_args_debug(self):
        """
        Test the --debug argument
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        with self.assertLogs(level='DEBUG') as cm:
            parser = target.parse_args(["--debug"])
        self.assertEqual(parser.loglevel, logging.DEBUG)
        self.assertEqual(parser.logging_level, "DEBUG")
        self.assertEqual(cm.output, ["DEBUG:root:These are the parsed " \
            "arguments:\n'Namespace(logging_level='DEBUG', loglevel=10)'"])

    def test_parse_args_version(self):
        """
        Test the --version argument
        """
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            parser = target.parse_args(["--version"])
        self.assertEqual(cm.exception.code, 0)
        self.assertTrue("scriptname.py 0.0.1-alpha" in f.getvalue())


class TestInit(unittest.TestCase):
    def test_init_no_param(self):
        """
        Test the init code without any parameters
        """
        target.__name__ = "__main__"
        target.sys.argv = ["scriptname.py", "--debug"]
        with self.assertLogs(level='DEBUG') as cm:
            target.init()
        self.assertEqual(cm.output, ["DEBUG:root:These are the parsed " \
            "arguments:\n'Namespace(logging_level='DEBUG', loglevel=10)'"])


class TestLicense(unittest.TestCase):
    def test_license_file(self):
        """
        Validate that the project has a LICENSE file, check part of its content
        """
        self.assertTrue(os.path.isfile("LICENSE"))
        with open('LICENSE') as f:
            s = f.read()
            # Confirm it is the MIT License
            self.assertTrue("MIT License" in s)
            self.assertTrue("Copyright (c) 2020 Emilien Klein" in s)

    def test_license_mention(self):
        """
        Validate that the script file contain a mention of the license
        """
        with open('billingflatfile.py') as f:
            s = f.read()
            # Confirm it is the MIT License
            self.assertTrue("#    This file is part of billingflatfile " \
                "and is MIT-licensed." in s)


if __name__ == '__main__':
    unittest.main()
