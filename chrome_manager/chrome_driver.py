# -*- coding: utf-8 -*-

"""A wharpper for chrome selenium."""

import logging
import sys
from os.path import expanduser, join, abspath, dirname
from random import random, randrange
from time import sleep

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    InvalidArgumentException,
    InvalidSessionIdException,
    JavascriptException,
    NoAlertPresentException,
    NoSuchElementException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER as SELENIUM_LOGGER
from urllib3.exceptions import MaxRetryError, NewConnectionError
from webdriver_manager.core.utils import ChromeType, get_browser_version_from_os

sys.path.append(abspath("."))

from chrome_manager.service import create_service

SELENIUM_LOGGER.setLevel(logging.ERROR)

LOG = logging.getLogger(__name__)


class ChromeSeleniumDrive:
    """Wrapper Chrome Selenium."""

    def __init__(
        self,
        service,
        headless=False,
        maximize=False,
        width=1280,
        height=700,
        user_data_dir=None,
        profile=None,
        silent=False,
    ) -> None:
        super().__init__()
        self.silent = silent

        self._driver = None
        self.headless = headless
        self.maximize = maximize
        self.service = service

        # https://peter.sh/experiments/chromium-command-line-switches/
        self.chrome_args = [
            # "--disable-notifications", # NÃO PASSA NAS PERMISSÕES
            "--disable-renderer-backgrounding",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            # "--no-proxy-server",
            # "--proxy-server='direct://'",
            # "--proxy-bypass-list=*",
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
            "--window-position=0,0",
            f"--window-size={width},{height}",
            f"--user-agent=Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{get_browser_version_from_os(ChromeType.GOOGLE)} Safari/537.36",
        ]

        if user_data_dir:
            if isinstance(user_data_dir, bool):
                user_data_dir = join(expanduser("~"), ".chrome_storage")
            self.chrome_args.append(rf"--user-data-dir={user_data_dir}")

        if profile:
            if isinstance(profile, bool):
                profile = "Default"
            self.chrome_args.append(rf"--profile-directory={profile}")

    def set_options(self, extensions=None, proxy=None):
        """Setup ChromeOptions."""
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"

        # https://tarunlalwani.com/post/selenium-disable-image-loading-different-browsers/
        chrome_prefs = dict()
        options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)
        # options.add_experimental_option("detach", True)
        if proxy:
            options.add_argument(f"--proxy-server=https://{proxy}")

        if self.headless:
            self.maximize = False
            self.chrome_args.append("--headless")

        for arg in self.chrome_args:
            options.add_argument(arg)

        if extensions:
            for ext in extensions:
                options.add_extension(ext)
        else:
            self.chrome_args.append("--disable-extensions")
        return options

    def create_driver(self, options=None) -> webdriver.Chrome:
        """Create a configured Chrome driver."""
        try:
            self._driver = webdriver.Chrome(
                service=self.service,
                options=options if options else self.set_options(),
            )
            if self.silent:
                LOG.info(
                    f"BROWSER_VERSION: {self._driver.capabilities['browserVersion']}"
                )
                LOG.info(
                    f"CHROME_DRIVER_VERSION: {self._driver.capabilities['chrome']['chromedriverVersion']}"
                )
        except InvalidArgumentException:
            print("")
            print("Aparentemente uma outra instancia do Chromium esta aberta, feche-a.")
            LOG.fatal(
                "Aparentemente uma outra instancia do Chromium esta aberta, feche-a."
            )
            print("")
            sys.exit(0)
        except KeyboardInterrupt:
            sys.exit(0)

        if self.maximize:
            print()
            print()
            LOG.info("Chrome iniciando Maximizado.")
            self._driver.maximize_window()
            # driver.minimize_window()

        return self._driver

    def wait_for_alert(self, wait_time=10) -> None | bool:
        """Aguarda um alert ser clicado."""
        while True:
            try:
                alert = self._driver.switch_to.alert
                LOG.info(f"Switch to Success! -> {alert}")
                return True
            except NoAlertPresentException:
                sleep(1)
                wait_time -= 1
            if wait_time <= 0:
                break
        return False

    def wait_for_selector(self, selector, wait_time=10, click=False) -> WebElement:
        """Wait for CSS and Selector."""
        counter = 0
        while counter < wait_time:
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
                ElementNotInteractableException,
            ):
                pass
            counter += 0.1
            sleep(1)

    def wait_for_selectors(self, selector, wait_time=10, click=False) -> WebElement:
        """Wait for CSS and Selector."""
        counter = 0
        while counter < wait_time:
            try:
                element = self._driver.find_elements(By.CSS_SELECTOR, selector)
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
                ElementNotInteractableException,
            ):
                pass
            counter += 1
            sleep(1)

    def wait_page_load(self, wait_time=2, verbose=True) -> bool:
        """Wait page complete load."""
        load_counter = 0
        states = ["complete"]
        while self._driver.execute_script("return document.readyState;") not in states:
            if load_counter == wait_time:
                break
            if verbose:
                print(self._driver.execute_script("return document.readyState;"))
            sleep(1)
            load_counter += 1
        return True

    def scrap_tab_two(self, url, wait_time=2) -> None | str:
        page_html = None
        self.wait_page_load(wait_time=5)
        try:
            if len(self._driver.window_handles) == 1:
                self._driver.execute_script("window.open()")

            if len(self._driver.window_handles) == 2:
                self._driver.switch_to.window(self._driver.window_handles[-1])
                self._driver.get(url)
                load_counter = 0
                while self._driver.execute_script(
                    "return document.readyState;"
                ) not in ["complete"]:
                    sleep(1)
                    if load_counter == 30:
                        self._driver.refresh()
                    elif load_counter == 45:
                        self._driver.execute_script("window.close()")
                    load_counter += 1
                else:
                    sleep(1)
                    page_html = self._driver.page_source
                    sleep(wait_time)
                    self._driver.execute_script("window.close()")
                if len(self._driver.window_handles) == 1:
                    self._driver.switch_to.window(self._driver.window_handles[-1])
                # return page_html
            return page_html
        except (JavascriptException, TimeoutError):
            pass
        except WebDriverException:
            self._driver.switch_to.window(self._driver.window_handles[-1])
        return None

    def close(self) -> None:
        """Close driver."""
        try:
            self._driver.close()
        except (
            ConnectionRefusedError,
            MaxRetryError,
            NewConnectionError,
            InvalidSessionIdException,
            WebDriverException,
        ):
            pass


def rand_time():
    """Return a random float number."""
    return random() * randrange(2)


if __name__ == "__main__":
    SET_DRIVER = ChromeSeleniumDrive(
        service=create_service(), maximize=True, headless=True
    )
    DRIVER = SET_DRIVER.create_driver()
    DRIVER.get(
        "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"
    )
    sleep(10)
    DRIVER.save_screenshot(join(dirname(abspath(".")), "teste.png"))
    SET_DRIVER.close()
    pass
