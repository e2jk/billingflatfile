# billingflatfile
Generate the required fixed width format files from delimited files extracts for EMR billing purposes


[![Latest release on GitHub](https://img.shields.io/github/v/release/e2jk/billingflatfile)](https://github.com/e2jk/billingflatfile/releases/latest)
[![Latest release on PyPI](https://img.shields.io/pypi/v/billingflatfile)](https://pypi.org/project/billingflatfile/)
[![Build Status](https://travis-ci.com/e2jk/billingflatfile.svg?branch=master)](https://travis-ci.com/e2jk/billingflatfile)
[![codecov](https://codecov.io/gh/e2jk/billingflatfile/branch/master/graph/badge.svg)](https://codecov.io/gh/e2jk/billingflatfile)
[![GitHub last commit](https://img.shields.io/github/last-commit/e2jk/billingflatfile.svg)](https://github.com/e2jk/billingflatfile/commits/master)
[![License](https://img.shields.io/github/license/e2jk/billingflatfile)](../../tree/master/LICENSE)

How to run the program
======================

How to install the program
--------------------------

For Linux and Windows, download the latest version from [here](https://github.com/e2jk/billingflatfile/releases/latest) (look under the "Assets" section) and run it on your system, no need to install anything else.

The program can also be installed from the Python Package Index:

```
pip install billingflatfile
```

Or it can be downloaded and ran directly from the [Docker Hub](https://hub.docker.com/r/e2jk/billingflatfile):

```
docker run --rm e2jk/billingflatfile [add parameters here]
```

See below [how to install from source](#how-to-install-from-source).

Configuration file
------------------

In order for the program to know how to transform your delimited file into a fixed-width file, you will need to provide a configuration file describing the length and type of values expected for your output file.

An example configuration file can be found at
[`tests/sample_files/configuration1.xlsx`](../../tree/master/tests/sample_files/configuration1.xlsx)

A configuration file is a simple Excel `.xlsx` file in which each row represents a single field expected in the output file (the fixed-width file), and at least these 3 column headers, i.e. the first line in your Excel file:

* Length
* Output format
* Skip field

The **Length** value is self-explanatory: it represents how long the field will be in the generated fixed-width file. If the value in the input file is shorter than this defined length, it will be padded with `0`s or spaces, depending on the type of Output format (see next section).

The **Output format** defines how the input value must be treated and transformed. The following values are supported:
* `Integer`
  * A numeric value that gets padded with `0`s added to the left
  * Example: "`123`" becomes "`000123`" if a length of 6 is defined
* `Decimal`
  * Decimal numbers get sent as "cents" instead of "dollars", rounded to the nearest cent. (yeah, weird explanation -- better have a look at the example...). Also padded with `0`s added to the left.
  * Example: "`123.458`" becomes "`00012346`" if a length of 8 is defined
* `Keep numeric`
  * strips all non-numeric characters from an input value and treats the remaining value as `Integer`
  * Example: "`1-2.3a`" becomes "`000123`" if a length of 6 is defined

* Date
  * A date to be converted from one format to another. The input value can be sent with either Day or Month as first element or as ISO format YYYYMMDD, and with a slash, dash, dot or no separator. When there is a separator defined, the day and month can omit the leading 0, if need be. See at the top of the [`test_main.py` file](https://github.com/e2jk/delimited2fixedwidth/blob/master/tests/test_main.py#L37) for the full list of supported codes.
  * Examples:
    * "`21/06/2020`" becomes "`20200621`" with a format of `Date (DD/MM/YYYY to YYYYMMDD)` and a length of 8
    * "`6-21-2020`" becomes "`20200621`" with a format of `Date (MM-DD-YYYY to YYYYMMDD)` and a length of 8
    * "`21062020`" becomes "`20200621`" with a format of `Date (DDMMYYYY to YYYYMMDD)` and a length of 8
    * "`6.21.2020`" becomes "`21/06/2020`" with a format of `Date (MM.DD.YYYY to DD/MM/YYYY)` and a length of 10
* `Time`
  * A time sent as hour:minutes (with or without colon in the input data) will be sent out without the colon
  * Example: "`20:06`" becomes "`2006`" if a length of 4 is defined
* `Text`
  * The value gets sent without format changes (such as those outlined above for date and time), with spaces added at the end, on the right of the string
  * Example: "`Hello`" becomes "<code>Hello&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</code>" if a length of 10 is defined

Finally, setting the value of the **Skip field** column to "`True`" allows to send a field as blank in the output file, respecting the field size and padding type: `0`s or spaces depending on the defined output format.


Running the program
-------------------

Open a Command Line window `cmd` and indicate your input file name and configuration file to use. You will also need to indicate a number of arguments needed to generate the metadata file, such as the Application ID and the Run ID.
You can additionally indicate if your input file uses a specific field separator (default is `,`), textual field wrapper (default is `"`), if you want to skip a specific number of header or footer files from your input file, a description for this billing run and the type of billing.

See the [Program help information](#program-help-information) section below for details on how to populate these arguments.

An example run of the program could look like this:

```
billingflatfile.exe --input data\input_file.txt --config data\configuration_file.xlsx --application-id AB --run-id 456 --skip-header 1 --skip-footer 1 --delimiter "^" --run-description "Nice description" --billing-type "H"
```

Or it can be ran from the [Docker Hub](https://hub.docker.com/r/e2jk/billingflatfile):

```
docker run --rm e2jk/billingflatfile [add parameters here]
```

If you've installed the program following [how to install from source](#how-to-install-from-source), you can run the program with `pipenv run python billingflatfile.py`.

Program help information
------------------------
```
usage: billingflatfile.py [-h] [--version] -i INPUT -c CONFIG [-dl DELIMITER] [-q QUOTECHAR] [-sh SKIP_HEADER]
                          [-sf SKIP_FOOTER] [-l LOCALE] [-t TRUNCATE] [-dv DIVERT] [-o OUTPUT_DIRECTORY] [-x] -a
                          APPLICATION_ID [-ds RUN_DESCRIPTION] [-b BILLING_TYPE] -r RUN_ID [-fv FILE_VERSION]
                          [-dr DATE_REPORT] [-d] [-v]

Generate the required fixed width format files from delimited files extracts for EMR billing purposes

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -i INPUT, --input INPUT
                        Specify the input file
  -c CONFIG, --config CONFIG
                        Specify the configuration file
  -dl DELIMITER, --delimiter DELIMITER
                        The field delimiter used in the input file (default ,)
  -q QUOTECHAR, --quotechar QUOTECHAR
                        The character used to wrap textual fields in the input file (default ")
  -sh SKIP_HEADER, --skip-header SKIP_HEADER
                        The number of header lines to skip (default 0)
  -sf SKIP_FOOTER, --skip-footer SKIP_FOOTER
                        The number of footer lines to skip (default 0)
  -l LOCALE, --locale LOCALE
                        Change the locale, useful to handle decimal separators
  -t TRUNCATE, --truncate TRUNCATE
                        Comma-delimited list of field numbers for which the output will be truncated at the maximum
                        line length, should the input value be longer than the maximum defined field length. If not
                        set, a field that is too long will cause the script to stop with an error.
  -dv DIVERT, --divert DIVERT
                        Diverts to a separate file the content from rows containing a specific value at a specific
                        place. The format of this parameter is "<field number>,<value to divert on>" (without quotes).
                        This parameter can be repeated several times to support different values or different fields.
                        The diverted content will be saved to a file whose name will be the output filename with
                        "_diverted" added before the file extension.
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        The directory in which to create the output files
  -x, --overwrite-files
                        Allow to overwrite the output files
  -a APPLICATION_ID, --application-id APPLICATION_ID
                        The application ID. From the vendor specs: the first character will be filled with the first
                        letter of the site that is to be invoiced, and the second character will be filled with a
                        significant letter to describe the application. Must be unique for the receiving application
                        to accept the files. Max 2 characters.
  -ds RUN_DESCRIPTION, --run-description RUN_DESCRIPTION
                        The description for this run. Free text, max 30 characters.
  -b BILLING_TYPE, --billing-type BILLING_TYPE
                        The billing type. Must be 'H' (internal billing), 'E' (external billing) or ' ' (both external
                        and internal billing, or undetermined). Max 1 character.
  -r RUN_ID, --run-id RUN_ID
                        The ID for this run. Must be unique for each run for the receiving application to accept it.
                        Numeric value between 0 and 99999, max 5 characters.
  -fv FILE_VERSION, --file-version FILE_VERSION
                        The version of the output file to be generated. Only 'V1.11' is currently supported. Max 8
                        characters.
  -dr DATE_REPORT, --date-report DATE_REPORT
                        The column number of a Date column to report on in the metadata file. Numeric value between 0
                        and 99999.
  -d, --debug           Print lots of debugging statements
  -v, --verbose         Be verbose
```

Development information
=======================

How to install from source
--------------------------

### Create the environment:
```bash
cd devel/billingflatfile/
python3 -m pip install --user pipenv
pipenv install
```

If you want to develop the script, replace that last command by `pipenv install --dev`

### Activate the virtual environment:
```bash
cd devel/billingflatfile/
pipenv shell
```

You can also run the script using `pipenv run billingflatfile.py` instead of `python3 billingflatfile.py` without having to set up a subshell (which has some problems in Windows, with the history not being accessible with the up arrow)

### When done:
```bash
exit
```

### Update the dependencies:
```bash
pipenv update
```

### Install a new dependency
```bash
pipenv install <package_name> [--dev]
```

Building the executable
-----------------------

Run the following command in your virtual environment:

```
pipenv run pyinstaller --onefile billingflatfile.py
```

The executable that gets created in the `dist` folder can then be uploaded to Github as a new release.

Packaging the source and publishing to the Python Package Index
---------------------------------------------------------------

Follow the instructions mentioned [here](https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives), namely:

```
pipenv lock -r > requirements-no-dev.txt
pipenv run python setup.py sdist bdist_wheel
pipenv run python -m twine upload dist/*
```

Create the Docker image and publish it to Docker Hub
----------------------------------------------------

Run:

* `docker build -t e2jk/billingflatfile:latest -t e2jk/billingflatfile:<version> --rm .` to build the Docker image.
* `docker run --rm e2jk/billingflatfile:<version>` to test the Docker image locally.
* `docker push e2jk/billingflatfile:<version>` to push the Docker image to Docker Hub.
