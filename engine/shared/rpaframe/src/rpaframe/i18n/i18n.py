import gettext
import locale
import os

from rpaframe.logger.logger import logger


class I18n:
    """国际化"""

    def __init__(self, name: str = "null"):
        """翻译失败,接受翻译文件不存在"""

        self.translation = None
        try:
            localedir = os.path.join(os.getcwd(), "translations")
            self.translation = gettext.translation(name, localedir=localedir, languages=["zh_CN"])
            locale.setlocale(locale.LC_ALL, "zh_CN.UTF-8")
        except Exception:
            logger.warning("翻译失败，接受翻译文件不存在")
            return

    def gettext(self, message):
        """翻译失败，接受翻译key不存在"""

        if self.translation is None:
            # 翻译文件不存在的优化
            return message

        try:
            return self.translation.gettext(message)
        except Exception:
            logger.warning("翻译失败，接受翻译key不存在")
            return message


_ = I18n("I18n").gettext
