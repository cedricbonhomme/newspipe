__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 9.0 $"
__date__ = "$Date: 2016/11/14 $"
__revision__ = "$Date: 2020/02/27 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import os
import subprocess

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

__version__ = (
    os.environ.get("PKGVER")
    or subprocess.run(["git",
                       "-C",
                       BASE_DIR,
                       "describe",
                       "--tags"], stdout=subprocess.PIPE)
    .stdout.decode()
    .strip()
)
