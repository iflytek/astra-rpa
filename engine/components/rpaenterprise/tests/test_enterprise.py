import platform
import sys
from unittest import TestCase

from rpaenterprise import ReportLevelType
from rpaenterprise.enterprise import Enterprise


class TestEnterprise(TestCase):
    def test_print(self):
        enterprise = Enterprise()
        res = enterprise.print(print_type=ReportLevelType.INFO, print_msg="hello")
        if sys.platform == "win32":
            self.assertEqual(res, "[info] win hello")
        elif platform.system() == "Linux":
            self.assertEqual(res, "[info] linux hello")

    def test_shareholder_upload(self):
        enterprise = Enterprise()
        enterprise.upload_to_sharefolder(r"D:\new-rpa2\data\logs\rpa_browser_connector-2025-08-21.log")

    def test_shareholder_download(self):
        enterprise = Enterprise()
        enterprise.download_from_sharefolder(file_path=1958825462281179136, save_folder=r"D:\new-rpa2\data")
