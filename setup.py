import sys
from setuptools import setup, find_packages

import sitekicker

if sys.version_info.major < 3:
    raise RuntimeError('This package only supports Python 3!')

setup(
    name='sitekicker',
    version=sitekicker.version,
    description=sitekicker.description,
    long_description='',
    url=sitekicker.url,
    download_url=sitekicker.url,
    author=sitekicker.author,
    author_email=sitekicker.email,
    license=sitekicker.license,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sitekicker = sitekicker.__main__:main',
        ],
    },
    install_requires=[
        'PyYAML',
        'Pygments',
        'beautifulsoup4',
        'markdown',
        'pymdown-extensions',
        'Jinja2',
        'watchdog',
        'Wand',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Topic :: System :: Networking',
        'Topic :: Terminals',
        'Topic :: Text Processing',
        'Topic :: Utilities'
    ]
)
