#!/usr/bin/env python3
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('version') as version_file:
    version = version_file.read()

with open('HISTORY.adoc') as history_file:
    history = history_file.read()

requirements = list()
with open('requirements.txt') as req:
    for i in req:
        requirements.append(i.strip())

requirements_dev = list()
with open('requirements_dev.txt') as req:
    for i in req:
        requirements_dev.append(i.strip())

setup(
    name='concsp',
    version=version,
    description="Concourse resource for salt pepper",
    long_description=readme + '\n\n' + history,
    author="dgengtek",
    author_email='dgengtek@gmail.com',
    url='https://devnull',
    entry_points={
        "console_scripts": [
            "concsp=concsp.cli.cli:main",
        ],
    },
    packages=find_packages("src"),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='concourse-salt-pepper',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
    test_suite='tests',
    tests_require=requirements_dev,
    setup_requires=[],
)
