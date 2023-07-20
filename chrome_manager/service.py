# -*- coding: utf-8 -*-

"""Create a webdriver service."""

import os

os.environ['WDM_LOG'] = '0'
os.environ['WDM_LOG_LEVEL'] = '0'
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def create_service():
    """Return a webdriver service."""
    return Service(ChromeDriverManager(version="115.0.5790.99").install())
