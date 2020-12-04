# -*- coding: utf-8 -*-
from pathlib import Path
from pkg_resources import get_distribution, DistributionNotFound

import os

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version

except DistributionNotFound:
    __version__ = 'unknown'

finally:
    del get_distribution, DistributionNotFound

PROJECT_ROOT = Path(Path(__file__).resolve().parents[1])
if str(PROJECT_ROOT).startswith(os.getcwd()):
    PROJECT_ROOT = PROJECT_ROOT.relative_to(os.getcwd())

SRC_ROOT = PROJECT_ROOT.joinpath('src')
