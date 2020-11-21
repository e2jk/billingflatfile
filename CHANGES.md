# Changelog
These are the changes brought in each versions:

v1.0.6 (TBD)
===================
Non-breaking changes:
---------------------

v1.0.5 (2020-11-21)
===================
Breaking changes:
-----------------
* `--output_directory` is now mandatory, don't create a default output directory in data/<today's date>
* Upper limit for the `--run-id` argument down from 99999 to 9999

Non-breaking changes:
---------------------
* Process all the files in a directory as multiple input files through the new arguments `--input-directory` and `--output-directory`
* New `--move-input-files` argument to move the input files to the output directory after processing
* New `--run-id-file` arguments to read and save the next Run ID. Allows for automated recurring runs, for instance associated with the `--input-directory` and `--move-input-files` arguments
* New `--input-encoding` argument to specify the encoding of the input files, defaults to 'utf-8'

v1.0.4 (2020-11-02)
===================
Breaking changes:
-----------------
* Date and Time fields now default/pad to 0's instead of spaces

Non-breaking changes:
---------------------
* New `--txt-extension` argument to add a `.txt` extension to the output files' names.
* The program can now be ran in a Docker container: https://hub.docker.com/r/e2jk/billingflatfile

v1.0.3 (2020-09-30)
===================
Non-breaking changes:
---------------------
* New `--truncate` argument to specify which fields can be cut when the input value is longer than the defined maximum field length
* New `--locale` argument, in case a different Decimal separator is used
* Fix: Spaces or empty string accepted as valid Integer and Decimal values (interpreted as 0)
* Support a large number of new date formats. See at the top of the [`test_main.py` file](https://github.com/e2jk/delimited2fixedwidth/blob/master/tests/test_main.py#L37) for the full list of supported codes. Some examples:
  * `Date (DD/MM/YYYY to DD/MM/YYYY)`
  * `Date (YYYYMMDD to DD.MM.YYYY)`
  * `Date (MM.DD.YYYY to YYYYMMDD)`
  * `Date (YYYYMMDD to MM-DD-YYYY)`
* New format `Keep numeric` that strips all non-numeric characters from an input value
* New `--divert` argument to divert to a separate file the content from rows containing specific values

v1.0.2 (2020-09-16)
===================
Non-breaking changes:
---------------------
* Support for new date formats:
  * `Date (DD-MM-YYYY to YYYYMMDD)`
  * `Date (MM-DD-YYYY to YYYYMMDD)`
  * `Date (DD.MM.YYYY to YYYYMMDD)`
  * `Date (MM.DD.YYYY to YYYYMMDD)`
  * `Date (DDMMYYYY to YYYYMMDD)`
  * `Date (MMDDYYYY to YYYYMMDD)`

v1.0.1 (2020-09-16)
===================
Other changes:
--------------
* Reduce the number of dependencies

v1.0.0 (2020-09-14)
===================
Non-breaking changes:
---------------------
* New `--date-report` argument

Other changes:
--------------
* Changes to the development toolchain and test suite

v0.0.1-alpha (2020-09-10)
=========================
* Initial release
