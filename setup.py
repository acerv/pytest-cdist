# -*- coding: utf-8 -*-
"""
setuptools script.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
from setuptools import setup, find_packages
from cdist import __version__

setup(
    name='pytest-cdist',
    version=__version__,
    description='Pytest plugin for distributed pytest configurations',
    author='Andrea Cervesato',
    author_email='andrea.cervesato@mailbox.org',
    url='https://github.com/acerv/pytest-cdist',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
    packages=["cdist"],
    python_version=">3.4,<3.9",
    install_requires=[
        'click<=7.0',
        'colorama<=0.4.3',
        'redis<=3.4.1',
    ],
    entry_points={
        'console_scripts': [
            'cdist-cli=cdist.command:cli',
        ],
        'pytest11': [
            'cdist = cdist.plugin',
        ]
    },
)
