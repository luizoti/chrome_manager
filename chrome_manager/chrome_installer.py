
import os
import sys

import tempfile
import subprocess

from os.path import exists, dirname, basename, join

import requests

WORK_DIR = dirname(__file__)

sys.path.insert(0, WORK_DIR)

from webdriver_manager.core.utils import get_browser_version_from_os, ChromeType


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
        self.installed_version = None
        try:
            browser_version = get_browser_version_from_os(ChromeType.GOOGLE)
            self.installed_version = [
                int(x) for x in browser_version.split(".")
            ] if browser_version else [0] * 3
        except AttributeError:
            pass

    def remote_version_info(self):
        """Get the remote chrome version form Google download page."""
        json_versions = requests.get(
            "https://omahaproxy.appspot.com/json"
        ).json()
        for item in json_versions:
            os_type = item['os']
            if os_type == "win64":
                versions = item['versions']
                for version in versions:
                    if version["channel"] == "stable":
                        return [
                            int(x) for x in version["current_version"].split(".")[:3]
                        ]

    def check(self):
        """Check if chrome need be updated."""
        print()
        print("-" * 45)
        print(
            "Versão instalada             :", "{}.{}.{}".format(
                *self.installed_version)
        )
        print(
            "Versão remota (para download):", "{}.{}.{}".format(
                *self.remote_version_info())
        )
        print("-" * 45)

        if not self.installed_version:
            print()
            print("Parece que o Chrome não esta instalado!")
            return True
        return any([k < y for k, y in zip(self.installed_version, self.remote_version_info())])


class ChromeDownloader():
    """Chrome Downloader."""

    def __init__(self) -> None:
        self.download_url = "https://dl.google.com/tag/s/appguid%3D%7B8A69D345-D564-463C-AFF1-A69D9E530F96%7D%26iid%3D%7B3F3CBD57-9859-7E36-5898-0AA5B15CF21C%7D%26lang%3Den%26browser%3D4%26usagestats%3D0%26appname%3DGoogle%2520Chrome%26needsadmin%3Dtrue%26ap%3Dx64-stable-statsdef_0%26brand%3DGCEJ/dl/chrome/install/googlechromestandaloneenterprise64.msi"

    def install(self, dest_dir=None):
        """Install Chrome."""

        if not ChromeNeedUpdate().check():
            print()
            print("Chrome já instalado e na ultima versão.")
            return

        print()
        print("Baixando a ultima versão do Chrome.")

        if not dest_dir:
            dest_dir = tempfile.gettempdir()

        downloaded_file = self.download_file(
            download_url=self.download_url,
            dest_dir=dest_dir,
            file_name="chromesetup.msi"
        )

        subprocess.call(["msiexec.exe", "/i", downloaded_file, "/qb"])
        return True

    def download_file(self, download_url, dest_dir=None, file_name=None):
        """Download file with url."""

        if not file_name:
            # Maybe is possible to ge extension from requests, maybe is to work
            file_name = basename(download_url)

        if not dest_dir:
            dest_dir = tempfile.gettempdir()

        dest_file = join(dest_dir, file_name)
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

    def sizeof_fmt(self, num, suffix="B"):
        """Format size for humans."""
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return f"{round(num, 1)} {unit} {suffix}"
            num /= 1024.0
        return f"{round(num, 1)} Yi {suffix}"


if __name__ == "__main__":
    ChromeDownloader().install()
