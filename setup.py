import setuptools

with open("README.md", "r") as fh:
    readme = fh.read()
with open("CHANGES.md", "r") as fh:
    changes = fh.read().replace("# Changelog", "Changelog\n=========\n")
long_description = "%s\n\n%s" % (readme, changes)

with open("requirements-no-dev.txt", "r") as fh:
    requirements = [line.rstrip() for line in fh if line.rstrip()]
    if requirements[0].startswith("-i http"):
        requirements.pop(0)

from billingflatfile import get_version

setuptools.setup(
    name="billingflatfile",
    version=get_version("__init__.py"),
    author="Emilien Klein",
    author_email="emilien@klein.st",
    description="Generate the required fixed width format files from "
    "delimited files extracts for EMR billing purposes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/e2jk/billingflatfile",
    py_modules=["billingflatfile"],
    install_requires=[req for req in requirements if req[:2] != "# "],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
