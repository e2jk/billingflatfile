coverage run --include=./*.py --omit=tests/*,.venv-billingflatfile/* -m unittest discover && \
rm -rf html_dev/coverage && \
coverage html --directory=html_dev/coverage --title="Code test coverage for billingflatfile"
