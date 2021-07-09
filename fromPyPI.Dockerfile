FROM python:3.9-slim

# Install billingflatfile from PyPI
RUN pip install --no-cache-dir billingflatfile

# Run the module and output the help text
RUN python -m billingflatfile --help
