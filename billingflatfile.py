#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This file is part of billingflatfile and is MIT-licensed.

import sys
import argparse
import logging
import re
import os
import delimited2fixedwidth

def parse_args(arguments):
    parser = argparse.ArgumentParser(description="Generate the required " \
        "fixed width format files from delimited files extracts for EMR " \
        "billing purposes")
    parser.add_argument('--version',
        action='version',
        version='%(prog)s 0.0.1-alpha'
    )

    delimited2fixedwidth.add_shared_args(parser)

    parser.add_argument("-o", "--output-directory",
        help="The directory in which to create the output files",
        action='store',
        required=True
    )
    parser.add_argument("-a", "--application-id",
        help="The application ID. From the vendor specs: the first " \
            "character will be filled with the first letter of the site that " \
            "is to be invoiced, and the second character will be filled with " \
            "a significant letter to describe the application. Must be " \
            "unique for the receiving application to accept the files.",
        action='store',
        required=True
    )
    parser.add_argument("-r", "--run-id",
        help="The ID for this run. Must be unique for each run for the " \
            "receiving application to accept it.",
        action='store',
        required=True
    )

    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    args = parser.parse_args(arguments)

    # Configure logging level
    if args.loglevel:
        logging.basicConfig(level=args.loglevel)
        args.logging_level = logging.getLevelName(args.loglevel)

    # Validate if the arguments are used correctly
    args.application_id = args.application_id.upper()
    m = re.match(r"^[A-Z0-9]{2}$", args.application_id)
    if not m:
        logging.critical("The `--application-id` argument must be two " \
            "characters, from 'AA' to '99'. Exiting...")
        sys.exit(212)

    try:
        args.run_id = int(args.run_id)
    except ValueError:
        logging.critical("The `--run-id` argument must be numeric. Exiting...")
        sys.exit(210)
    if args.run_id < 0 or args.run_id > 9999:
        logging.critical("The `--run-id` argument must be comprised between " \
            "0 and 9999. Exiting...")
        sys.exit(211)
    args.run_id = str(args.run_id).zfill(4)

    delimited2fixedwidth.validate_shared_args(args)

    logging.debug("These are the parsed arguments:\n'%s'" % args)
    return args

def init():
    if __name__ == "__main__":
        # Parse the provided command-line arguments
        args = parse_args(sys.argv[1:])

        if not os.path.isdir(args.output_directory):
            os.mkdir(args.output_directory)
        metadata_file_name = "%s/S%s%sE" % (args.output_directory,
            args.application_id, args.run_id)
        logging.debug("The metadata file will be written to '%s'" %
            metadata_file_name)
        detailed_file_name = "%s/S%s%sD" % (args.output_directory,
            args.application_id, args.run_id)
        logging.debug("The detailed file will be written to '%s'" %
            detailed_file_name)
        #TODO: check if these files don't exist, create --overwrite-file arg

        # Run the delimited2fixedwidth main process
        # Generates the main file with the detailed transactions
        (num_input_rows, oldest_date, most_recent_date) = \
            delimited2fixedwidth.process(args.input, detailed_file_name,
            args.config, args.delimiter, args.quotechar, args.skip_header,
            args.skip_footer)

        # Generate the second file containing the metadata

init()
