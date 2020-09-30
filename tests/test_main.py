#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Running the tests:
# $ python3 -m unittest discover --start-directory ./tests/
# Checking the coverage of the tests:
# $ coverage run --include=./*.py --omit=tests/* -m unittest discover && \
#   rm -rf html_dev/coverage && coverage html --directory=html_dev/coverage \
#   --title="Code test coverage for billingflatfile"

import contextlib
import io
import logging
import os
import pathlib
import shutil
import sys
import unittest
from datetime import date
from locale import Error as localeError

CURRENT_VERSION = "1.0.3"

sys.path.append(".")
target = __import__("billingflatfile")


class TestGetVersion(unittest.TestCase):
    def test_get_version_valid(self):
        """
        Test the script's version
        """
        version = target.get_version("__init__.py")
        self.assertEqual(CURRENT_VERSION, version)

    def test_get_version_invalid_file(self):
        """
        Test the Exception when getting the version from an invalid file
        """
        with self.assertRaises(RuntimeError) as cm:
            target.get_version("LICENSE")
        self.assertEqual(str(cm.exception), "Unable to find version string.")

    def test_get_version_nonexistent_file(self):
        """
        Test the Exception when getting the version from a nonexistent file
        """
        nonexistent_file = "tests/sample_files/nonexistent_test_output.txt"
        # Confirm the output file doesn't exist
        if os.path.isfile(nonexistent_file):
            os.remove(nonexistent_file)
            self.assertFalse(os.path.isfile(nonexistent_file))
        with self.assertRaises(FileNotFoundError) as cm:
            target.get_version(nonexistent_file)
        expected_output = "[Errno 2] No such file or directory: '%s'" % nonexistent_file
        self.assertEqual(str(cm.exception), expected_output)


class TestPadOutputValue(unittest.TestCase):
    def test_pad_output_value_numeric(self):
        """
        Test padding a numeric output value
        """
        val = target.pad_output_value("123", "numeric", 5, "Field Name")
        self.assertEqual(val, "00123")

    def test_pad_output_value_alphanumeric(self):
        """
        Test padding an alphanumeric output value
        """
        val = target.pad_output_value("123", "alphanumeric", 5, "Field Name")
        self.assertEqual(val, "123  ")

    def test_pad_output_value_too_long(self):
        """
        Test padding output value, too long input value
        """
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.pad_output_value("TOO LONG", None, 2, "Field Name")
        self.assertEqual(cm1.exception.code, 214)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Field 'Field Name' for metadata file is too long! "
                "Length: 8, max length 2. Exiting..."
            ],
        )

    def test_pad_output_value_nonnumeric_number(self):
        """
        Test padding output value, passing a non-numeric value for a
        numeric field
        """
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.pad_output_value("NOT A NUMBER", "numeric", 15, "Field Name")
        self.assertEqual(cm1.exception.code, 215)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:A non-numeric value was passed for the numeric "
                "'Field Name' metadata file field. Exiting..."
            ],
        )

    def test_pad_output_value_invalid_output_format(self):
        """
        Test padding output value, passing an invalid output_format
        """
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.pad_output_value("", "INVALID", 15, "Field Name")
        self.assertEqual(cm1.exception.code, 216)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Unsupported output format 'INVALID' for metadata "
                "file field 'Field Name'. Exiting..."
            ],
        )


class TestGenerateMetadataFile(unittest.TestCase):
    def test_generate_metadata_file_invalid_version(self):
        """
        Test generating the metadata file with an invalid output file version
        """
        file_version = "INVALID"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.generate_metadata_file(
                "application_id",
                "run_description",
                "oldest_date",
                "most_recent_date",
                "billing_type",
                "num_input_rows",
                "run_id",
                file_version,
            )
        self.assertEqual(cm1.exception.code, 213)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Unsupported output file version 'INVALID', must be "
                "one of 'V1.11'. Exiting..."
            ],
        )

    def test_generate_metadata_file(self):
        """
        Test generating the metadata file
        """
        application_id = "AA"
        run_description = "BB"
        oldest_date = "20200620"
        most_recent_date = "20201129"
        billing_type = "E"
        num_input_rows = "17"
        run_id = "345"
        file_version = "V1.11"
        output = target.generate_metadata_file(
            application_id,
            run_description,
            oldest_date,
            most_recent_date,
            billing_type,
            num_input_rows,
            run_id,
            file_version,
        )
        self.assertEqual(
            output,
            "SAABB                            "
            "2020062020201129E00001700345V1.11                             "
            "                                                              "
            "                                           ",
        )


class TestParseArgs(unittest.TestCase):
    def test_parse_args_no_arguments(self):
        """
        Test running the script without any of the required arguments
        """
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(f):
            target.parse_args([])
        self.assertEqual(cm.exception.code, 2)
        self.assertTrue(
            "error: the following arguments are required: -i/--input, "
            "-c/--config, -a/--application-id, -r/--run-id" in f.getvalue()
        )

    def test_parse_args_valid_arguments(self):
        """
        Test running the script with all the required arguments
        """
        input_file = "tests/sample_files/input1.txt"
        config_file = "tests/sample_files/configuration1.xlsx"
        parser = target.parse_args(
            [
                "--input",
                input_file,
                "--run-id",
                "123",
                "--config",
                config_file,
                "--application-id",
                "SE",
            ]
        )
        self.assertEqual(parser.input, input_file)
        self.assertEqual(
            parser.output_directory, os.path.join("data", date.today().isoformat())
        )
        self.assertEqual(parser.config, config_file)
        self.assertEqual(parser.application_id, "SE")
        self.assertEqual(parser.run_description, "")
        self.assertEqual(parser.billing_type, " ")
        self.assertEqual(parser.run_id, "0123")
        self.assertEqual(parser.loglevel, logging.WARNING)
        self.assertEqual(parser.logging_level, "WARNING")

    def test_parse_args_debug(self):
        """
        Test the --debug argument
        """
        input_file = "tests/sample_files/input1.txt"
        output_directory = "data"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertLogs(level="DEBUG") as cm:
            parser = target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "--debug",
                    "--application-id",
                    "SE",
                    "--run-id",
                    "123",
                ]
            )
        self.assertEqual(parser.loglevel, logging.DEBUG)
        self.assertEqual(parser.logging_level, "DEBUG")
        self.maxDiff = None
        self.assertEqual(
            cm.output,
            [
                "DEBUG:root:These are the parsed arguments:\n'Namespace("
                "application_id='SE', "
                "billing_type=' ', "
                "config='tests/sample_files/configuration1.xlsx', "
                "date_report=None, "
                "delimiter=',', "
                "divert=[], "
                "file_version='V1.11', "
                "input='tests/sample_files/input1.txt', "
                "locale='', "
                "logging_level='DEBUG', "
                "loglevel=10, "
                "output_directory='data', "
                "overwrite_files=False, "
                "quotechar='\"', "
                "run_description='', "
                "run_id='0123', "
                "skip_footer=0, "
                "skip_header=0, "
                "truncate=[])'"
            ],
        )

    def test_parse_args_invalid_input_file(self):
        """
        Test running the script with a non-existent input file as -i parameter
        """
        input_file = "tests/sample_files/nonexistent_input.txt"
        output_directory = "data"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "--application-id",
                    "SE",
                    "--run-id",
                    "123",
                ]
            )
        self.assertEqual(cm1.exception.code, 10)
        self.assertEqual(
            cm2.output,
            ["CRITICAL:root:The specified input file does not exist. Exiting..."],
        )

    def test_parse_args_invalid_config_file(self):
        """
        Test running the script with a non-existent config file as -c parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_directory = "data"
        config_file = "tests/sample_files/nonexistent_configuration.xlsx"
        # Confirm the config file doesn't exist
        self.assertFalse(os.path.isfile(config_file))
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "--application-id",
                    "SE",
                    "--run-id",
                    "123",
                ]
            )
        self.assertEqual(cm1.exception.code, 12)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The specified configuration file does not exist. "
                "Exiting..."
            ],
        )

    def test_parse_args_skip_header_str(self):
        """
        Test running the script with an invalid --skip-header parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_directory = "data"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "-sh",
                    "INVALID",
                    "--application-id",
                    "SE",
                    "--run-id",
                    "123",
                ]
            )
        self.assertEqual(cm1.exception.code, 21)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The `--skip-header` argument must be numeric. "
                "Exiting..."
            ],
        )

    def test_parse_args_skip_footer_str(self):
        """
        Test running the script with an invalid --skip-footer parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_directory = "data"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "-sf",
                    "INVALID",
                    "--application-id",
                    "SE",
                    "--run-id",
                    "123",
                ]
            )
        self.assertEqual(cm1.exception.code, 22)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The `--skip-footer` argument must be numeric. "
                "Exiting..."
            ],
        )

    def test_parse_args_application_id_str(self):
        """
        Test running the script with an invalid --application-id parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_directory = "data"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "--application-id",
                    "INVALID",
                    "--run-id",
                    "123",
                ]
            )
        self.assertEqual(cm1.exception.code, 212)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The `--application-id` argument must be two "
                "characters, from 'AA' to '99'. Exiting..."
            ],
        )

    def test_parse_args_billing_type_invalid(self):
        """
        Test running the script with invalid --billing-type parameters
        """
        input_file = "tests/sample_files/input1.txt"
        output_directory = "data"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "--application-id",
                    "AA",
                    "--billing-type",
                    "INVALID",
                    "--run-id",
                    "123",
                ]
            )
        self.assertEqual(cm1.exception.code, 217)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The `--billing-type` argument must be one "
                "character, 'H' (internal billing), 'E' (external billing) or ' ' "
                "(both external and internal billing, or undetermined). "
                "Exiting..."
            ],
        )

    def test_parse_args_run_id_str(self):
        """
        Test running the script with an invalid --run-id parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_directory = "data"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "--application-id",
                    "SE",
                    "--run-id",
                    "INVALID",
                ]
            )
        self.assertEqual(cm1.exception.code, 210)
        self.assertEqual(
            cm2.output,
            ["CRITICAL:root:The `--run-id` argument must be numeric. Exiting..."],
        )

    def test_parse_args_run_id_too_big(self):
        """
        Test running the script with a --run-id parameter that's too large
        """
        input_file = "tests/sample_files/input1.txt"
        output_directory = "data"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "--application-id",
                    "SE",
                    "--run-id",
                    "123456",
                ]
            )
        self.assertEqual(cm1.exception.code, 211)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The `--run-id` argument must be comprised between "
                "0 and 99999. Exiting..."
            ],
        )

    def test_parse_args_date_report_str(self):
        """
        Test running the script with an invalid --run-id parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_directory = "data"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "--application-id",
                    "SE",
                    "--run-id",
                    "456",
                    "--date-report",
                    "INVALID",
                ]
            )
        self.assertEqual(cm1.exception.code, 221)
        self.assertEqual(
            cm2.output,
            ["CRITICAL:root:The `--date-report` argument must be numeric. Exiting..."],
        )

    def test_parse_args_date_report_too_big(self):
        """
        Test running the script with a --run-id parameter that's too large
        """
        input_file = "tests/sample_files/input1.txt"
        output_directory = "data"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "--application-id",
                    "SE",
                    "--run-id",
                    "456",
                    "--date-report",
                    "123456",
                ]
            )
        self.assertEqual(cm1.exception.code, 222)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The `--date-report` argument must be comprised between "
                "0 and 99999. Exiting..."
            ],
        )

    def test_parse_args_file_version_invalid(self):
        """
        Test running the script with an invalid --file-version parameter
        """
        input_file = "tests/sample_files/input1.txt"
        output_directory = "data"
        config_file = "tests/sample_files/configuration1.xlsx"
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.parse_args(
                [
                    "--input",
                    input_file,
                    "--output-directory",
                    output_directory,
                    "--config",
                    config_file,
                    "--application-id",
                    "SE",
                    "--run-id",
                    "123",
                    "--file-version",
                    "INVALID",
                ]
            )
        self.assertEqual(cm1.exception.code, 218)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:Incorrect `--file-version` argument value "
                "'INVALID', currently only 'v1.11' is supported. Exiting..."
            ],
        )

    def test_parse_args_version(self):
        """
        Test the --version argument
        """
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(f):
            target.parse_args(["--version"])
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
        self.assertTrue(
            "error: the following arguments are required: -i/--input, "
            "-c/--config, -a/--application-id, -r/--run-id" in f.getvalue()
        )

    def test_init_existing_metadata_file(self):
        """
        Test the init code with existing metadata file, without the
        --overwrite-files argument
        """
        application_id = "SE"
        run_id = "0123"
        output_directory = "existing_directory"
        metadata_file_name = os.path.join(
            output_directory, "S%s%sE" % (application_id, run_id)
        )
        pathlib.Path(output_directory).mkdir(parents=True, exist_ok=True)
        self.assertTrue(os.path.isdir(output_directory))
        pathlib.Path(metadata_file_name).touch()
        self.assertTrue(os.path.isfile(metadata_file_name))

        target.__name__ = "__main__"
        target.sys.argv = [
            "scriptname.py",
            "--input",
            "tests/sample_files/input1.txt",
            "--output-directory",
            output_directory,
            "--config",
            "tests/sample_files/configuration1.xlsx",
            "--delimiter",
            "^",
            "--skip-header",
            "1",
            "--skip-footer",
            "1",
            "--application-id",
            application_id,
            "--run-description",
            "AAA",
            "--billing-type",
            "H",
            "--run-id",
            run_id,
        ]
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.init()

        self.assertEqual(cm1.exception.code, 219)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The metadata output file '%s' does already exist, "
                "will NOT be overwritten. Add the `--overwrite-files` argument to "
                "overwrite. Exiting..." % metadata_file_name
            ],
        )
        shutil.rmtree(output_directory)
        self.assertFalse(os.path.isdir(output_directory))

    def test_init_existing_detailed_file(self):
        """
        Test the init code with existing detailed file, without the
        --overwrite-files argument
        """
        application_id = "SE"
        run_id = "0123"
        output_directory = "existing_directory"
        detailed_file_name = os.path.join(
            output_directory, "S%s%sD" % (application_id, run_id)
        )
        pathlib.Path(output_directory).mkdir(parents=True, exist_ok=True)
        self.assertTrue(os.path.isdir(output_directory))
        pathlib.Path(detailed_file_name).touch()
        self.assertTrue(os.path.isfile(detailed_file_name))

        target.__name__ = "__main__"
        target.sys.argv = [
            "scriptname.py",
            "--input",
            "tests/sample_files/input1.txt",
            "--output-directory",
            output_directory,
            "--config",
            "tests/sample_files/configuration1.xlsx",
            "--delimiter",
            "^",
            "--skip-header",
            "1",
            "--skip-footer",
            "1",
            "--application-id",
            application_id,
            "--run-description",
            "AAA",
            "--billing-type",
            "H",
            "--run-id",
            run_id,
        ]
        with self.assertRaises(SystemExit) as cm1, self.assertLogs(
            level="CRITICAL"
        ) as cm2:
            target.init()

        self.assertEqual(cm1.exception.code, 220)
        self.assertEqual(
            cm2.output,
            [
                "CRITICAL:root:The detailed output file '%s' does already exist, "
                "will NOT be overwritten. Add the `--overwrite-files` argument to "
                "overwrite. Exiting..." % detailed_file_name
            ],
        )
        shutil.rmtree(output_directory)
        self.assertFalse(os.path.isdir(output_directory))

    def test_init_valid(self):
        """
        Test the init code with valid parameters
        """
        output_directory = "nonexistent_dir"
        self.assertFalse(os.path.isdir(output_directory))
        target.__name__ = "__main__"
        target.sys.argv = [
            "scriptname.py",
            "--input",
            "tests/sample_files/input1.txt",
            "--output-directory",
            output_directory,
            "--config",
            "tests/sample_files/configuration1.xlsx",
            "--delimiter",
            "^",
            "--skip-header",
            "1",
            "--skip-footer",
            "1",
            "--application-id",
            "SE",
            "--run-description",
            "AAA",
            "--billing-type",
            "H",
            "--run-id",
            "123",
            "--locale",
            "fr_FR.utf8",
        ]
        try:
            target.init()
        except localeError:
            # On Windows, the French locale is just called "fr"
            target.sys.argv[-1] = "fr"
            target.init()

        self.assertTrue(os.path.isdir(output_directory))

        # Confirm the output files have been written and their content
        metadata_file_name = "%s/SSE0123E" % output_directory
        self.assertTrue(os.path.isfile(metadata_file_name))
        with open(metadata_file_name) as f:
            s = f.read()
            expected_output = (
                "SSEAAA                           "
                "9999999900000000H00000300123V1.11                          "
                "                                                           "
                "                                                 "
            )
            self.assertEqual(expected_output, s)
        # Remove the metadata output file
        os.remove(metadata_file_name)
        self.assertFalse(os.path.isfile(metadata_file_name))

        detailed_file_name = "%s/SSE0123D" % output_directory
        self.assertTrue(os.path.isfile(detailed_file_name))
        with open(detailed_file_name) as f:
            s = f.read()
            expected_output = (
                "0004000133034205413540000100202007312006"
                "                                        "
                "Leendert MOLENDIJK [90038979]           \n"
                "0004000133034005407940000157202003051022"
                "                                        "
                "Leendert MOLENDIJK [90038979]           \n"
                "0004000133034105409340022139202012252006"
                "                                        "
                "Leendert MOLENDIJK [90038979]           "
            )
            self.assertEqual(expected_output, s)
        # Remove the detailed output file
        os.remove(detailed_file_name)
        self.assertFalse(os.path.isfile(detailed_file_name))
        shutil.rmtree(output_directory)
        self.assertFalse(os.path.isdir(output_directory))


class TestLicense(unittest.TestCase):
    def test_license_file(self):
        """
        Validate that the project has a LICENSE file, check part of its content
        """
        self.assertTrue(os.path.isfile("LICENSE"))
        with open("LICENSE") as f:
            s = f.read()
            # Confirm it is the MIT License
            self.assertTrue("MIT License" in s)
            self.assertTrue("Copyright (c) 2020 Emilien Klein" in s)

    def test_license_mention(self):
        """
        Validate that the script file contain a mention of the license
        """
        with open("billingflatfile.py") as f:
            s = f.read()
            # Confirm it is the MIT License
            self.assertTrue(
                "#    This file is part of billingflatfile and is MIT-licensed." in s
            )


if __name__ == "__main__":
    unittest.main()
