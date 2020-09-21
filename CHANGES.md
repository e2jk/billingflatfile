# Changelog
These are the changes brought in each versions:

v1.0.3 (TBD)
===================
Non-breaking changes:
---------------------
* New `--truncate` argument to specify which fields can be cut when the input value is longer than the defined maximum field length
* New `--locale` argument, in case a different Decimal separator is used
* Fix: Spaces or empty string accepted as valid Integer and Decimal values (interpreted as 0)

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
