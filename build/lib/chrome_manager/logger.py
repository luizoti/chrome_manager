# -*- coding: utf-8 -*-
# pylint: disable=logging-fstring-interpolation

"""Module with base log config."""

import logging
from os.path import dirname, join

LOG_FILE_PATH = join(dirname(dirname(__file__)), 'logfile.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    filename=LOG_FILE_PATH,
    encoding="utf8"
)
