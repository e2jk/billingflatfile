#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This file is part of billingflatfile and is MIT-licensed.

import sys
import argparse
import logging
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

        # Run the delimited2fixedwidth main process
        (num_input_rows, oldest_date, most_recent_date) = \
            delimited2fixedwidth.process(args.input, args.output, args.config,
            args.delimiter, args.quotechar, args.skip_header, args.skip_footer)

init()
