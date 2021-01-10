@echo off
coverage run --include=./*.py --omit=tests/*,.venv-billingflatfile/* -m unittest discover || EXIT /B 1
flake8 billingflatfile.py --statistics --count || EXIT /B 1
flake8 tests --statistics --count || EXIT /B 1
rd /s /q html_dev\coverage
coverage html --directory=html_dev\coverage --title="Code test coverage for billingflatfile"
coverage xml
