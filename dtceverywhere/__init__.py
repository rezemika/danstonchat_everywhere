"""
    A program to read DansTonChat quotes offline and in command line.
"""

__version__ = "0.1.0"
__appname__ = "danstonchat_everywhere"
__author__ = "rezemika <reze.mika@gmail.com>"
__licence__ = "AGPLv3"

import sys as _sys
import os as _os
_sys.path.append(_os.path.dirname(_os.path.abspath(__file__)))

from dtceverywhere.main import main
