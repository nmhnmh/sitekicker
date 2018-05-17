import sys
from setuptools import setup, find_packages

import sitekicker

if sys.version_info.major < 3 or sys.version_info.minor<5:
    raise RuntimeError('This package only supports Python 3.5+!')

setup()
