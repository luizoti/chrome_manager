
import os
import zipfile
import tempfile
import subprocess
from os.path import exists

from os.path import basename, join

import requests
from webdriver_manager.utils import get_browser_version_from_os, ChromeType


class OSType():
    """Return the os type."""
    LINUX = "linux"
    MAC = "mac"
    WIN = "win"

class ChromeArch():
    """Return arch strings to format url."""
    X32 = ("-arch_x86", "GoogleChromeEnterpriseBundle.zip")
    X64 = ("x64-", "GoogleChromeEnterpriseBundle64.zip")


class ChromeNeedUpdate():
    """Detect if Chrome Need update."""

    def __init__(self) -> None:
        self.installed_version = get_browser_version_from_os(ChromeType.GOOGLE)

    def remote_version_info(self):
        """Get the remote chrome version form Google download page."""
        json_versions = requests.get("https://omahaproxy.appspot.com/json").json()
        for item in json_versions:
            os_type = item['os']
            if os_type == "win64":
                versions = item['versions']
                for version in versions:
                    if version["channel"] == "stable":
                        return version["current_version"]

    def check(self):
        """Compare installed and remote Chrome versions."""
        if self.installed_version in self.remote_version_info():
            return False
        return True


class WebSignerInstaller():
    """Chrome Downloader."""

    def __init__(self) -> None:
        self.base_url = "https://get.websignerplugin.com/Downloads/2.9.0/setup-win-pt"


    def install(self, dest_dir=None):
        """Install Chrome."""

        if not dest_dir:
            dest_dir = tempfile.gettempdir()

        downloaded_file = self.download_file(self.base_url)
        subprocess.run(
            [
                "msiexec.exe", "/passive", "/i",
                downloaded_file
            ],
            check=True,
            shell=False
        )
        return True

    def download_file(self, extension_url, dest_dir=None, file_name=None):
        """Download file with url."""

        if not file_name:
            # Maybe is possible to ge extension from requests, maybe is to work
            file_name = basename(extension_url)

        if not dest_dir:
            dest_dir = tempfile.gettempdir()

        dest_file = join(dest_dir, file_name)
        if exists(dest_file):
            return dest_file

        with open(dest_file, "wb") as binary_file:
            print()
            response = requests.get(extension_url, stream=True)
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

    def sizeof_fmt(self, num, suffix="B"):
        """Format size for humans."""
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return f"{round(num, 1)}{unit}{suffix}"
            num /= 1024.0
        return f"{round(num, 1)}Yi{suffix}"


if __name__ == "__main__":
    WebSignerInstaller().install()
