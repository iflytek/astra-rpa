import base64
import datetime
import io
import os
import subprocess
import sys
from typing import Any, Tuple

import pyautogui


class Screenshot:
    @staticmethod
    def screenshot(region: Tuple[int, int, int, int] = (0, 0, 0, 0), file_path: str = "") -> Any:
        """
        截图
        """
        if sys.platform == "win32":
            return pyautogui.screenshot(file_path, region=region)
        else:
            st = Screenshot.screenshot_linux(file_path, region=region)
            img_byte_arr = io.BytesIO()
            st.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()
            base64_image = base64.b64encode(img_byte_arr).decode("utf-8")
            return base64_image

    @staticmethod
    def screenshot_linux(imageFilename=None, region=None):
        """见pyautogui"""

        if imageFilename is None:
            tmp_filename = ".screenshot%s.png" % (datetime.datetime.now().strftime("%Y-%m%d_%H-%M-%S-%f"))
        else:
            tmp_filename = imageFilename

        subprocess.call(["scrot", "-z", tmp_filename])
        from PIL import Image

        im = Image.open(tmp_filename)

        if region is not None:
            assert len(region) == 4, "region argument must be a tuple of four ints"
            assert (
                isinstance(region[0], int)
                and isinstance(region[1], int)
                and isinstance(region[2], int)
                and isinstance(region[3], int)
            ), "region argument must be a tuple of four ints"
            im = im.crop((region[0], region[1], region[2] + region[0], region[3] + region[1]))
            os.unlink(tmp_filename)  # delete image of entire screen to save cropped version
            im.save(tmp_filename)
        else:
            # force loading before unlinking, Image.open() is lazy
            im.load()

        if imageFilename is None:
            os.unlink(tmp_filename)
        return im
