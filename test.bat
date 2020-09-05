@echo off
coverage run --include=./*.py --omit=tests/*,.venv-billingflatfile/* -m unittest discover || EXIT /B 1
rd /s /q html_dev\coverage
coverage html --directory=html_dev\coverage --title="Code test coverage for billingflatfile"
