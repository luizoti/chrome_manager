#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Python Script to download the Chrome Extensions (CRX) file directly from the google chrome web store.
    Referred from http://chrome-extension-downloader.com/how-does-it-work.php
"""

import os
import re
import sys
import tempfile
import platform
from pathlib import Path

import requests
from urllib.parse import urlparse
from os.path import basename, exists
from webdriver_manager.core.utils import get_browser_version_from_os, ChromeType


ARCH = platform.architecture()


class ChromeExtensionDownloader():
    """Class to download Chrome Extension by URL."""

    def __init__(self):
        self.ext_download_url = "https://clients2.google.com/service/update2/crx?response=redirect&prodversion={chrome_version}&acceptformat=crx2,crx3&x=id%3D{extension_id}%26uc&nacl_arch={arch}"

    def download(self, chrome_store_url, version_string=get_browser_version_from_os(ChromeType.GOOGLE)):
        """
            Download the given URL into given filename.
            :param chrome_store_url:
            :param _file_name_:
            :return:
        """
        arch = self.get_arch()
        extension_id, file_name = self.parse_extension_url(
            chrome_store_url=chrome_store_url
        )
        # chrome_version = self.get_chrome_version(user_agent_ver)

        extension_url = self.ext_download_url.format(
            chrome_version=version_string,
            extension_id=extension_id,
            arch=arch
        )
        return extension_url, self.download_file(
            download_url=extension_url,
            dest_dir=None,
            file_name=file_name + ".crx"
        )

    def parse_extension_url(self, chrome_store_url):
        """
            Validate the given input is chrome store URL or not.
            Returning app ID and app Name from the URL
            :param chrome_store_url:
            :return:
        """
        try:
            # Try to validate the URL
            uparse = urlparse(chrome_store_url)

            if uparse.netloc != "chrome.google.com":
                raise ValueError(f"Not a valid URL {chrome_store_url}")

            splits = uparse.path.split("/")

            if not uparse.path.startswith("/webstore/detail/"):
                raise ValueError(f"Not a valid URL {chrome_store_url}")
        except ValueError as value_error:
            raise value_error
        return splits[-1], splits[-2]

    def sizeof_fmt(self, num, suffix="B"):
        """Format size for humans."""
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, "Yi", suffix)

    def download_file(self, download_url, dest_dir=None, file_name=None):
        """Download file with url."""

        if not file_name:
            # Maybe is possible to ge extension from requests, maybe is to work
            file_name = basename(download_url)

        if not dest_dir:
            dest_dir = tempfile.gettempdir()

        dest_file = Path(dest_dir, file_name)
        if exists(dest_file):
            os.remove(path=dest_file)
            print(f"Arquivo deletado: {dest_file}")

        with open(dest_file, "wb") as binary_file:
            print()
            response = requests.get(download_url, stream=True)
            total = response.headers.get("content-length")

            if total is None:
                binary_file.write(response.content)
                return False
            else:
                downloaded = 0
                total = int(total)
                try:
                    for data in response.iter_content(chunk_size=max(int(total / 1000), 1024 * 1024)):
                        downloaded += len(data)
                        binary_file.write(data)
                        done = int(50 * downloaded / total)
                        str_to_format = f"\rBaixando: {dest_file} {'█' * done}{'.' * (50 - done)} | {self.sizeof_fmt(downloaded)}/{self.sizeof_fmt(total)}"
                        print(str_to_format, end="\r")
                        if downloaded == total:
                            return dest_file
                except KeyboardInterrupt:
                    print("\nDonwload interrompido")
                    return False
                print()

    def get_arch(self):
        """Return a compatible architecture to use in download url."""
        if "64bit" in ARCH:
            return 'x86-64'
        elif "32bit" in ARCH:
            return 'x86-32'
        else:
            print("Not inplemented")
            sys.exit(0)

    def get_chrome_version(self, chrome_version):
        """Extract get_chrome version from User Agent."""
        from_user_agent = re.findall(
            r"Chrom(?:e|ium)\/(\d+)\.(\d+)\.(\d+)\.(\d+)", chrome_version)

        if from_user_agent:
            return ".".join(from_user_agent[0])
        elif re.match(r"\d+\.\d+\.\d+", chrome_version):
            return chrome_version


if __name__ == '__main__':
    url = "https://chrome.google.com/webstore/detail/certisign-websigner/acfifjfajpekbmhmjppnmmjgmhjkildl"
    downloader = ChromeExtensionDownloader().download(url)
    print(downloader)
