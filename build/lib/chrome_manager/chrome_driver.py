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
    NoSuchElementException,
    NoAlertPresentException,
    WebDriverException
)

from selenium.webdriver.remote.remote_connection import LOGGER as SELENIUM_LOGGER
from urllib3.exceptions import MaxRetryError, NewConnectionError


from selenium import webdriver
from selenium.webdriver.common.by import By

from chrome_manager.service import create_service


WORK_DIR = dirname(dirname(__file__))

sys.path.insert(0, WORK_DIR)

import chrome_manager.logger as LOG

from webdriver_manager.utils import get_browser_version_from_os, ChromeType

SELENIUM_LOGGER.setLevel(logging.WARNING)
LOG = logging.getLogger(__name__)

class ChromeSeleniumDrive():
    """Wraper Chrome selenium."""

    def __init__(self, service, headless=False, maximize=False, width=1280, height=700, chrome_storage_path=None, silent=False) -> None:
        super().__init__()
        # TODO: silent argumento temporario, não pode continuar assim
        self.silent = silent

        self._driver = None
        self.headless = headless
        self.maximize = maximize
        self.service = service

        if chrome_storage_path:
            self.chrome_storage = join(
                chrome_storage_path, "chrome_persistence_config")
        # https://peter.sh/experiments/chromium-command-line-switches/
        self.chrome_args = [
            # "--disable-notifications", # NÃO PASSA NAS PERMISSÔES
            # "--disable-renderer-backgrounding",
            # "--disable-background-timer-throttling",
            # "--disable-backgrounding-occluded-windows",
            # "--disable-extensions",
            "--no-proxy-server",
            "--proxy-server='direct://'",
            "--proxy-bypass-list=*",
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
            rf"--profile-directory={basename(__file__)}",
        ]

        if chrome_storage_path:
            self.chrome_args.append(rf"--user-data-dir={self.chrome_storage}")

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
        # options.add_experimental_option("detach", True)

        if self.headless:
            self.maximize = False
            self.chrome_args.append("--headless")

        for arg in self.chrome_args:
            options.add_argument(arg)

        if extensions:
            for ext in extensions:
                options.add_extension(ext)

        try:
            self._driver = webdriver.Chrome(
                service=self.service,
                options=options,
            )
            if self.silent:
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

        return options

    def create_driver(self, options=None) -> webdriver.Chrome:
        """Create a configured Chrome driver."""

        if not options:
            options = self.set_options()

        if self.maximize:
            print()
            print()
            print("Chrome iniciando Maximizado.")
            self._driver.maximize_window()
            # driver.minimize_window()

        return self._driver

    def wait_for_alert(self, random=False):
        """Agarda um alert ser clicado."""
        alert_presente = True
        while True:
            try:
                self._driver.switch_to.alert
                sleep(1 + rand_time() if random else 0)
            except NoAlertPresentException:
                alert_presente = False
                break
        return alert_presente

    def wait_for_selector(self, selector, wait_time=10, random=False, click=False):
        """Wait for CSS and Selector."""
        counter = 0
        while counter <= wait_time:
            try:
                element = self._driver.find_element(By.CSS_SELECTOR, selector)
                if element:
                    if click:
                        element.click()
                    return element
            except (
                WebDriverException,
                NoSuchElementException,
                ElementNotInteractableException,
                ElementClickInterceptedException,
                InvalidSessionIdException,
                JavascriptException,
                ElementNotInteractableException
            ):
                pass
            counter += 1
            sleep(1 + rand_time() if random else 0)

    def wait_page_load(self, wait_time=2):
        """Wait page complete load."""
        counter = 0
        states = ["complete"]
        while self._driver.execute_script("return document.readyState;") not in states:
            if counter >= wait_time:
                break
            sleep(1)
            counter += 1
        return True

    def scrap_tab_two(self, url, wait_time=2, random=False):
        page_html = None
        if len(self._driver.window_handles) == 1:
            self._driver.execute_script("window.open()")

        sleep(wait_time + rand_time() if random else 0)
        if len(self._driver.window_handles) == 2:
            self._driver.switch_to.window(self._driver.window_handles[-1])
            self._driver.get(url)
            while self._driver.execute_script("return document.readyState;") not in ["interactive", "complete"]:
                sleep(0.2)
                print(self._driver.execute_script(
                    "return document.readyState;"))
                pass
            else:
                sleep(1)
                page_html = self._driver.page_source
                sleep(wait_time + rand_time() if random else 0)
                self._driver.execute_script("window.close()")
            if len(self._driver.window_handles) == 1:
                self._driver.switch_to.window(self._driver.window_handles[-1])
            return page_html
        return None

    def close(self):
        try:
            self._driver.close()
        except (
            ConnectionRefusedError,
            MaxRetryError,
            NewConnectionError,
            InvalidSessionIdException,
            WebDriverException
        ):
            pass

def rand_time():
    """Return a random float number."""
    return random() * randrange(2)


if __name__ == "__main__":
    SET_DRIVER = ChromeSeleniumDrive(service=create_service(),maximize=True, headless=False)
    DRIVER = SET_DRIVER.create_driver()
    DRIVER.get(
        "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"
    )
    sleep(10)
    SET_DRIVER.close()
    pass