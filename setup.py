#!/usr/bin/env python
# Filename: setup.py
"""
The setup script.

"""
from setuptools import setup
import sys
import json

pinfo = json.loads(open("codemeta.js", "r").read())

def read_stripped_lines(filename):
    """Return a list of stripped lines from a file"""
    with open(filename) as fobj:
        return [l.strip() for l in fobj.readlines()]

slug = "surveyer"

try:
    with open("README.md") as fh:
        long_description = fh.read()
except UnicodeDecodeError:
    long_description = pinfo["description"]

setup(
    name=slug,
    url=pinfo["codeRepository"],
    description=pinfo["description"],
    long_description=long_description,
    author=pinfo["author"][0]["givenName"]+" "+pinfo["author"][0]["familyName"],
    author_email=pinfo["author"][0]["email"],
    packages=[slug],
    include_package_data=True,
    platforms='any',
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    python_requires='>=3.5',
    install_requires=read_stripped_lines("requirements.txt"),
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
    ],
)
