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
import tempfile

CURRENT_VERSION = "0.0.1-alpha"

sys.path.append('.')
target = __import__("billingflatfile")


class TestParseArgs(unittest.TestCase):
    def test_parse_args_no_arguments(self):
        """
        Test running the script without any of the required arguments
        """
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(f):
            parser = target.parse_args([])
        self.assertEqual(cm.exception.code, 2)
        self.assertTrue("error: the following arguments are required: " \
            "-i/--input, -o/--output, -c/--config" in f.getvalue())

    def test_parse_args_valid_arguments(self):
        """
        Test running the script with all the required arguments
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        parser = target.parse_args(["-i", input_file, "-o", output_file,
            "-c", config_file])
        self.assertEqual(parser.input, input_file)
        self.assertEqual(parser.config, config_file)
        self.assertEqual(parser.loglevel, logging.WARNING)
        self.assertEqual(parser.logging_level, "WARNING")

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
            parser = target.parse_args(["-i", input_file, "-o", output_file,
                "-c", config_file, "--debug"])
        self.assertEqual(parser.loglevel, logging.DEBUG)
        self.assertEqual(parser.logging_level, "DEBUG")
        self.assertEqual(cm.output, ["DEBUG:root:These are the parsed " \
            "arguments:\n'Namespace(config='tests/sample_files/configuration1" \
            ".xlsx', delimiter=',', input='tests/sample_files/input1.txt', " \
            "logging_level='DEBUG', loglevel=10, output='tests/sample_files/" \
            "nonexistent_test_output.txt', overwrite_file=False, " \
            "quotechar='\"', skip_footer=0, skip_header=0)'"])

    def test_parse_args_invalid_input_file(self):
        """
        Test running the script with a non-existent input file as -i parameter
        """
        input_file = "tests/sample_files/nonexistent_input.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        # Confirm the input file doesn't exist
        self.assertFalse(os.path.isfile(input_file))
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            parser = target.parse_args(["-i", input_file, "-o", output_file,
                "-c", config_file])
        self.assertEqual(cm1.exception.code, 10)
        self.assertEqual(cm2.output, ["CRITICAL:root:The specified input " \
            "file does not exist. Exiting..."])

    def test_parse_args_invalid_config_file(self):
        """
        Test running the script with a non-existent config file as -c parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/nonexistent_configuration.xlsx"
        # Confirm the output file doesn't exist
        if os.path.isfile(output_file):
            os.remove(output_file)
            self.assertFalse(os.path.isfile(output_file))
        # Confirm the config file doesn't exist
        self.assertFalse(os.path.isfile(config_file))
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            parser = target.parse_args(["-i", input_file, "-o", output_file,
                "-c", config_file])
        self.assertEqual(cm1.exception.code, 12)
        self.assertEqual(cm2.output, ["CRITICAL:root:The specified " \
            "configuration file does not exist. Exiting..."])

    def test_parse_args_existing_output_file_no_overwrite(self):
        """
        Test running the script with an existing output file and without the
        --overwrite-file parameter
        """
        input_file = "tests/sample_files/input1.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        # Create a temporary file and confirm it exists
        (temp_fd, temp_output_file) = tempfile.mkstemp()
        self.assertTrue(os.path.isfile(temp_output_file))
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            parser = target.parse_args(["-i", input_file,
                "-o", temp_output_file, "-c", config_file])
        self.assertEqual(cm1.exception.code, 11)
        self.assertEqual(cm2.output, ['CRITICAL:root:The specified output file '
            'does already exist, will NOT overwrite. Add the `--overwrite-file`'
            ' argument to allow overwriting. Exiting...'])
        # Delete the temporary file created by the test
        os.close(temp_fd)
        os.remove(temp_output_file)

    def test_parse_args_skip_header_str(self):
        """
        Test running the script with an invalid --skip-header parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            parser = target.parse_args(["-i", input_file,
                "-o", output_file, "-c", config_file, "-sh", "INVALID"])
        self.assertEqual(cm1.exception.code, 21)
        self.assertEqual(cm2.output, ['CRITICAL:root:The `--skip-header` ' \
            'argument must be numeric. Exiting...'])

    def test_parse_args_skip_footer_str(self):
        """
        Test running the script with an invalid --skip-footer parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_file = "tests/sample_files/nonexistent_test_output.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, \
            self.assertLogs(level='CRITICAL') as cm2:
            parser = target.parse_args(["-i", input_file,
                "-o", output_file, "-c", config_file, "-sf", "INVALID"])
        self.assertEqual(cm1.exception.code, 22)
        self.assertEqual(cm2.output, ['CRITICAL:root:The `--skip-footer` ' \
            'argument must be numeric. Exiting...'])

    def test_parse_args_version(self):
        """
        Test the --version argument
        """
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            parser = target.parse_args(["--version"])
        self.assertEqual(cm.exception.code, 0)
        self.assertTrue("scriptname.py %s" % CURRENT_VERSION in f.getvalue())


class TestInit(unittest.TestCase):
    def test_init_no_param(self):
        """
        Test the init code without any parameters
        """
        target.__name__ = "__main__"
        target.sys.argv = ["scriptname.py"]
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(f):
            target.init()
        self.assertEqual(cm.exception.code, 2)
        self.assertTrue("error: the following arguments are required: " \
            "-i/--input, -o/--output, -c/--config" in f.getvalue())

    def test_init_valid(self):
        """
        Test the init code with valid parameters
        """
        (temp_fd, output_file) = tempfile.mkstemp()
        self.assertTrue(os.path.isfile(output_file))
        target.__name__ = "__main__"
        target.sys.argv = ["scriptname.py",
            "--input", "tests/sample_files/input1.txt",
            "--output", output_file,
            "--overwrite-file",
            "--config", "tests/sample_files/configuration1.xlsx",
            "--delimiter", "^",
            "--skip-header", "1",
            "--skip-footer", "1"]
        target.init()
        # Confirm the output file has been written and its content
        self.assertTrue(os.path.isfile(output_file))
        with open(output_file) as f:
            s = f.read()
            expected_output = "0004000133034205413540000100202007312006" \
                    "                                        " \
                    "Leendert MOLENDIJK [90038979]           \n" \
                "0004000133034005407940000157202003051022" \
                    "                                        " \
                    "Leendert MOLENDIJK [90038979]           \n" \
                "0004000133034105409340022139202012252006" \
                    "                                        " \
                    "Leendert MOLENDIJK [90038979]           "
            self.assertEqual(expected_output, s)
        # Remove the output file
        os.close(temp_fd)
        os.remove(output_file)
        self.assertFalse(os.path.isfile(output_file))


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
