#!/usr/bin/env python3
from setuptools import setup, find_packages

with open('README.adoc') as readme_file:
    readme = readme_file.read()

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
    name='concourse-salt-pepper',
    version='0.0.1',
    description="Concourse resource for salt pepper",
    long_description=readme + '\n\n' + history,
    author="dgengtek",
    author_email='dgengtek@gmail.com',
    url='https://devnull',
    entry_points={
        "console_scripts": [
            "concourse_check = concourse-salt-pepper.cli.cli:main",
            "concourse_in = concourse-salt-pepper.cli.cli:main",
            "concourse_out = concourse-salt-pepper.cli.cli:main",
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
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=requirements_dev,
    setup_requires=[],
)
