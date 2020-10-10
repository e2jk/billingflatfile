#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This file is part of billingflatfile and is MIT-licensed.

import argparse
import logging
import os
import pathlib
import re
import sys
from datetime import date

import delimited2fixedwidth


def get_version(rel_path):
    with open(rel_path) as f:
        for line in f.read().splitlines():
            if line.startswith("__version__"):
                return line.split('"')[1]
        else:
            raise RuntimeError("Unable to find version string.")


def save_metadata_file(output_content, output_file):
    with open(output_file, "w") as ofile:
        ofile.write(output_content)


def pad_output_value(val, output_format, length, field_name):
    val = str(val)
    if len(val) > length:
        logging.critical(
            "Field '%s' for metadata file is too long! Length: %d, max length %d. "
            "Exiting..." % (field_name, len(val), length)
        )
        sys.exit(214)
    if output_format == "numeric":
        # Confirm that field is actually a number
        try:
            int(val)
        except ValueError:
            logging.critical(
                "A non-numeric value was passed for the numeric '%s' metadata file "
                "field. Exiting..." % field_name
            )
            sys.exit(215)
        # Numbers get padded with 0's added in front (to the left)
        val = val.zfill(length)
    elif output_format == "alphanumeric":
        # Strings get padded with spaces added to the right
        format_template = "{:<%d}" % length
        val = format_template.format(val)
    else:
        logging.critical(
            "Unsupported output format '%s' for metadata file field '%s'. Exiting..."
            % (output_format, field_name)
        )
        sys.exit(216)
    return val


def generate_metadata_file(
    application_id,
    run_description,
    oldest_date,
    most_recent_date,
    billing_type,
    num_input_rows,
    run_id,
    file_version,
):
    output = ""
    supported_file_versions = ["V1.11"]
    if file_version not in supported_file_versions:
        logging.critical(
            "Unsupported output file version '%s', must be one of '%s'. Exiting..."
            % (file_version, "', '".join(supported_file_versions))
        )
        sys.exit(213)
    # 1 - application_id, 3 alphanumeric character
    output = pad_output_value(
        "S%s" % application_id, "alphanumeric", 3, "application_id"
    )
    # 2 - run_description, 30 alphanumeric character
    output += pad_output_value(run_description, "alphanumeric", 30, "run_description")
    # 3 - oldest_date, 8 numeric character
    output += pad_output_value(oldest_date, "numeric", 8, "oldest_date")
    # 4 - most_recent_date, 8 numeric character
    output += pad_output_value(most_recent_date, "numeric", 8, "most_recent_date")
    # 5 - billing_type, 1 alphanumeric character
    output += pad_output_value(billing_type, "alphanumeric", 1, "billing_type")
    # 6 - num_input_rows, 6 numeric character
    output += pad_output_value(num_input_rows, "numeric", 6, "num_input_rows")
    # 7 - run_id, 5 numeric character
    output += pad_output_value(run_id, "numeric", 5, "run_id")
    # 8 - file_version, 8 alphanumeric character
    output += pad_output_value(file_version, "alphanumeric", 8, "file_version")
    # 9 - filler, 131 alphanumeric character
    output += pad_output_value("", "alphanumeric", 131, "padding")

    logging.debug("Metadata content:\n%s" % output)

    return output


def parse_args(arguments):
    parser = argparse.ArgumentParser(
        description="Generate the required fixed width format files from delimited "
        "files extracts for EMR billing purposes"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%s %s" % ("%(prog)s", get_version("__init__.py")),
    )

    delimited2fixedwidth.add_shared_args(parser)

    parser.add_argument(
        "-o",
        "--output-directory",
        help="The directory in which to create the output files",
        action="store",
        required=False,
    )
    parser.add_argument(
        "-x",
        "--overwrite-files",
        help="Allow to overwrite the output files",
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "-a",
        "--application-id",
        help="The application ID. From the vendor specs: the first character will be "
        "filled with the first letter of the site that is to be invoiced, and the "
        "second character will be filled with a significant letter to describe the "
        "application. Must be unique for the receiving application to accept the "
        "files. Max 2 characters.",
        action="store",
        required=True,
    )
    parser.add_argument(
        "-ds",
        "--run-description",
        help="The description for this run. Free text, max 30 characters.",
        action="store",
        required=False,
        default="",
    )
    parser.add_argument(
        "-b",
        "--billing-type",
        help="The billing type. Must be 'H' (internal billing), 'E' (external billing) "
        "or ' ' (both external and internal billing, or undetermined). Max 1 "
        "character.",
        action="store",
        required=False,
        default=" ",
    )
    parser.add_argument(
        "-r",
        "--run-id",
        help="The ID for this run. Must be unique for each run for the receiving "
        "application to accept it. Numeric value between 0 and 99999, max 5 "
        "characters.",
        action="store",
        required=True,
    )
    parser.add_argument(
        "-fv",
        "--file-version",
        help="The version of the output file to be generated. Only 'V1.11' is "
        "currently supported. Max 8 characters.",
        action="store",
        required=False,
        default="V1.11",
    )
    parser.add_argument(
        "-dr",
        "--date-report",
        help="The column number of a Date column to report on in the metadata file. "
        "Numeric value between 0 and 99999.",
        action="store",
        required=False,
        default=None,
    )
    parser.add_argument(
        "-txt",
        "--txt-extension",
        help="Add a .txt extension to the output files' names.",
        action="store_true",
        required=False,
    )

    parser.add_argument(
        "-d",
        "--debug",
        help="Print lots of debugging statements",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    args = parser.parse_args(arguments)

    # Configure logging level
    if args.loglevel:
        logging.basicConfig(level=args.loglevel)
        args.logging_level = logging.getLevelName(args.loglevel)

    # Validate if the arguments are used correctly
    if not args.output_directory:
        # Default output dir: data/<today's date>
        args.output_directory = os.path.join("data", date.today().isoformat())
    if not os.path.isdir(args.output_directory):
        pathlib.Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    args.application_id = args.application_id.upper()
    m = re.match(r"^[A-Z0-9]{2}$", args.application_id)
    if not m:
        logging.critical(
            "The `--application-id` argument must be two characters, from 'AA' to "
            "'99'. Exiting..."
        )
        sys.exit(212)

    args.billing_type = args.billing_type.upper()
    if args.billing_type not in ("H", "E", " "):
        logging.critical(
            "The `--billing-type` argument must be one character, 'H' (internal "
            "billing), 'E' (external billing) or ' ' (both external and internal "
            "billing, or undetermined). Exiting..."
        )
        sys.exit(217)

    args.file_version = args.file_version.upper()
    if args.file_version not in ("V1.11",):
        logging.critical(
            "Incorrect `--file-version` argument value '%s', currently only 'v1.11' is "
            "supported. Exiting..." % args.file_version
        )
        sys.exit(218)

    try:
        args.run_id = int(args.run_id)
    except ValueError:
        logging.critical("The `--run-id` argument must be numeric. Exiting...")
        sys.exit(210)
    if args.run_id < 0 or args.run_id > 99999:
        logging.critical(
            "The `--run-id` argument must be comprised between 0 and 99999. Exiting..."
        )
        sys.exit(211)
    args.run_id = str(args.run_id).zfill(4)

    if args.date_report:
        try:
            args.date_report = int(args.date_report)
        except ValueError:
            logging.critical("The `--date-report` argument must be numeric. Exiting...")
            sys.exit(221)
        if args.date_report < 0 or args.date_report > 99999:
            logging.critical(
                "The `--date-report` argument must be comprised between 0 and 99999. "
                "Exiting..."
            )
            sys.exit(222)

    delimited2fixedwidth.validate_shared_args(args)

    logging.debug("These are the parsed arguments:\n'%s'" % args)
    return args


def init():
    if __name__ == "__main__":
        # Parse the provided command-line arguments
        args = parse_args(sys.argv[1:])

        metadata_file_name = os.path.join(
            args.output_directory, "S%s%sE" % (args.application_id, args.run_id)
        )
        detailed_file_name = os.path.join(
            args.output_directory, "S%s%sD" % (args.application_id, args.run_id)
        )
        if args.txt_extension:
            metadata_file_name += ".txt"
            detailed_file_name += ".txt"
        logging.debug("The metadata file will be written to '%s'" % metadata_file_name)
        logging.debug("The detailed file will be written to '%s'" % detailed_file_name)
        if os.path.isfile(metadata_file_name) and not args.overwrite_files:
            logging.critical(
                "The metadata output file '%s' does already exist, will NOT be "
                "overwritten. Add the `--overwrite-files` argument to overwrite. "
                "Exiting..." % metadata_file_name
            )
            sys.exit(219)
        if os.path.isfile(detailed_file_name) and not args.overwrite_files:
            logging.critical(
                "The detailed output file '%s' does already exist, will NOT be "
                "overwritten. Add the `--overwrite-files` argument to overwrite. "
                "Exiting..." % detailed_file_name
            )
            sys.exit(220)

        # Run the delimited2fixedwidth main process
        # Generates the main file with the detailed transactions
        (num_input_rows, oldest_date, most_recent_date) = delimited2fixedwidth.process(
            args.input,
            detailed_file_name,
            args.config,
            args.delimiter,
            args.quotechar,
            args.skip_header,
            args.skip_footer,
            args.date_report,
            args.locale,
            args.truncate,
            args.divert,
        )
        logging.info(
            "Processed %d rows, oldest date %s, most recent date %s"
            % (num_input_rows, oldest_date, most_recent_date)
        )

        # Generate the second file containing the metadata
        output = generate_metadata_file(
            args.application_id,
            args.run_description,
            oldest_date,
            most_recent_date,
            args.billing_type,
            num_input_rows,
            args.run_id,
            args.file_version,
        )
        save_metadata_file(output, metadata_file_name)
        logging.info("Metadata file written, end of the process")


init()
