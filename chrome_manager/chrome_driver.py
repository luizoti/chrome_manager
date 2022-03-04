# -*- coding: utf-8 -*-

"""Browser automation to login and store the qconcursos search with filters."""

import sys
import logging

from time import sleep
from os.path import join, dirname, basename
from random import random, randrange

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    InvalidSessionIdException,
    InvalidArgumentException,
    JavascriptException,
    NoSuchElementException
)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


WORK_DIR = dirname(dirname(dirname(__file__)))

sys.path.insert(0, WORK_DIR)

from .chrome_installer import ChromeArch, ChromeDownloader
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import get_browser_version_from_os, ChromeType

import lib.logger as LOG
LOG = logging.getLogger(__name__)

class ChromeSeleniumDrive():
    """Wraper Chrome selenium."""

    def __init__(self, headless=False, maximize=False, width=1280, height=800) -> None:
        super().__init__()
        self._driver = None
        self.headless = headless
        self.maximize = maximize
        ChromeDownloader().install()
        self.service = Service(ChromeDriverManager().install())

        self.chrome_storage = join(WORK_DIR, "chrome_persistence_config")
        # https://peter.sh/experiments/chromium-command-line-switches/
        self.chrome_args = [
            # "--disable-notifications", # NÃO PASSA NAS PERMISSÔES
            # "--disable-renderer-backgrounding",
            # "--disable-background-timer-throttling",
            # "--disable-backgrounding-occluded-windows",
            # "--disable-extensions",
            "--disable-popup-blocking",
            "--disable-accelerated-2d-canvas",
            "--disable-gpu",
            "--disable-breakpad",
            "--disable-features=TranslateUI,BlinkGenPropertyTrees,ChromeWhatsNewUI",
            "--disable-ipc-flooding-protection",
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-infobars",
            # "--minimal",
            # "--incognito",
            # "--single-process", # NUNCA USAR, ERRO EM MODO JANELA
            # "--start-in-incognito",
            # "--allow-insecure-localhost",
            "--enable-javascript",
            "--suppress-message-center-popups",
            "--ignore-certificate-errors",
            "--force-color-profile=srgb",
            "--mute-audio",
            "--metrics-recording-only",
            "--hide-scrollbars",
            "--ignore-certificate-errors",
            "--allow-running-insecure-content",
            "--no-sandbox",
            "--window-position=0,0",
            f"--window-size={width},{height}",
            f"--user-agent=Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{get_browser_version_from_os(ChromeType.GOOGLE)} Safari/537.36",
            rf"--user-data-dir={self.chrome_storage}",
            rf"--profile-directory={basename(__file__)}",
        ]

    def set_options(self, extensions=None):
        """Setup ChromeOptions."""
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"

        # https://tarunlalwani.com/post/selenium-disable-image-loading-different-browsers/
        chrome_prefs = {}
        options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("detach", True)

        if self.headless:
            self.maximize = False
            self.chrome_args.append("--headless")

        for arg in self.chrome_args:
            options.add_argument(arg)

        if extensions:
            for ext in extensions:
                options.add_extension(ext)
        return options

    def create_driver(self, options=None) -> webdriver.Chrome:
        """Create a configured Chrome driver."""

        if not options:
            options = self.set_options()

        try:
            self._driver = webdriver.Chrome(
                service=self.service,
                options=options,
            )
            LOG.info(
                f"BROWSERVERSION: {self._driver.capabilities['browserVersion']}"
            )
            LOG.info(
                f"CHROMEDRIVERVERSION: {self._driver.capabilities['chrome']['chromedriverVersion']}"
            )
        except InvalidArgumentException:
            print("")
            print("Aparentemente uma outra instancia do Chromium esta aberta, feche-a.")
            LOG.fatal(
                "Aparentemente uma outra instancia do Chromium esta aberta, feche-a.")
            print("")
            sys.exit(0)
        except KeyboardInterrupt:
            sys.exit(0)

        if self.maximize:
            print()
            print()
            print("Chrome iniciando Maximizado.")
            self._driver.maximize_window()
            # driver.minimize_window()

        return self._driver

    def wait_for_selector(self, selector, wait_time=10, click=False):
        """Wait for CSS and Selector."""
        counter = 0
        while counter < wait_time:
            try:
                element = self._driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    if click:
                        element.click()
                    return True
            except (
                NoSuchElementException,
                ElementNotInteractableException,
                ElementClickInterceptedException,
                InvalidSessionIdException,
                JavascriptException,
                ElementNotInteractableException
            ):
                pass
            counter += 1
            sleep(0.5)


def rand_time():
    """Return a random float number."""
    return random() * randrange(10)


if __name__ == "__main__":
    MYDRIVER = ChromeSeleniumDrive(maximize=True)
    driver = MYDRIVER.create_driver()
    driver.get("https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html")
    sleep(10)
