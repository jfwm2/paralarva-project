#!/usr/bin/env python3


import os
from setuptools import setup, find_packages


def _read_reqs(rel_path):
    full_path = os.path.join(os.path.dirname(__file__), rel_path)
    with open(full_path) as f:
        return [s.strip() for s in f.readlines()
                if (s.strip() and not s.startswith('#'))]


_REQUIREMENTS_TXT = _read_reqs('requirements.txt')
_INSTALL_REQUIRES = [requirement for requirement in _REQUIREMENTS_TXT
                     if '://' not in requirement]

with open(os.path.join('VERSION')) as version_file:
    version = version_file.read().strip()

setup(
    name='paralarva',
    version=version,
    install_requires=_INSTALL_REQUIRES,
    tests_require=_read_reqs('tests-requirements.txt'),
    dependency_links=[],
    data_files=[('.', ['requirements.txt', 'tests-requirements.txt'])],
    package_dir={"": "src"},
    packages=find_packages(where='src'),
)
