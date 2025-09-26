import ast
import os.path
import typing
from base64 import b64decode
from datetime import datetime

from dateutil import parser

from rpaatomic import TimeFormatType
from rpaatomic.error import *
from rpaatomic.types_manager import TypesManager

typesMg = TypesManager()
Any = typing.Any


class Float(float):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, Float):
            return value
        try:
            if isinstance(value, str):
                if value.lower() == "":
                    return cls(0)
            return cls(float(value))
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class Int(int):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, Int):
            return value
        try:
            if isinstance(value, str):
                if value.lower() == "":
                    return cls(0)
            return cls(int(value))
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class Bool:
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, Bool):
            return value
        try:
            if isinstance(value, str):
                if value.lower() in ["false", "none", "undefined"]:
                    return cls(False)
            return cls(bool(value))
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e

    def __init__(self, value: bool):
        if not isinstance(value, bool):
            raise BaseException(TYPE_KIND_ERROR_FORMAT.format(value), "Value must be a boolean")
        self._value = value

    def __bool__(self):
        return self._value

    def __str__(self):
        return str(self._value)


class Str(str):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, Str):
            return value
        try:
            return cls(str(value))
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class List(list):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, List):
            return value
        try:
            if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
                return ast.literal_eval(value)
            return cls(list(value))
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class Dict(dict):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, Dict):
            return value
        try:
            if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                return ast.literal_eval(value)
            return cls(dict(value))
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class PATH(Str):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, PATH):
            return value
        try:
            temp_value = str(value)
            temp_value = temp_value.strip()
            return cls(temp_value)
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e

    @typesMg.shortcut("PATH", "Str")
    def root(self):
        return os.path.splitdrive(self)[0]

    @typesMg.shortcut("PATH", "Str")
    def directory(self):
        return os.path.dirname(self)

    @typesMg.shortcut("PATH", "Str")
    def file_name(self):
        return os.path.basename(self)

    @typesMg.shortcut("PATH", "Str")
    def file_name_without_extension(self):
        return os.path.splitext(os.path.basename(self))[0]

    @typesMg.shortcut("PATH", "Str")
    def file_extension(self):
        return os.path.splitext(self)[1]


class DIRPATH(Str):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, DIRPATH):
            return value
        try:
            temp_value = str(value)
            temp_value = temp_value.strip()
            return cls(temp_value)
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e

    @typesMg.shortcut("DIRPATH", "Str")
    def root(self):
        return os.path.splitdrive(self)[0]

    @typesMg.shortcut("DIRPATH", "Str")
    def directory(self):
        return os.path.dirname(self)


class Date:
    """Date（时间）对象"""

    def __init__(self, time_str: str = None):
        self.time = datetime.now()
        if time_str:
            self.set_time(time_str=time_str)
        self.format = TimeFormatType.YMD_HMS

    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, Date):
            return value
        elif isinstance(value, str):
            try:
                return cls(time_str=value)
            except ValueError:
                raise BaseException(
                    PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                    "{}参数验证失败{}".format(name, value),
                )

        raise BaseException(
            PARAM_VERIFY_ERROR_FORMAT.format(name, value),
            "{}参数验证失败{}".format(name, value),
        )

    def set_time(self, time_str: str, format_type: TimeFormatType = TimeFormatType.YMD_HMS):
        self.format = format_type
        self.time = parser.parse(time_str)

    def __str__(self):
        if self.format in [
            TimeFormatType.YMD_CN,
            TimeFormatType.YMD_CN_HM,
            TimeFormatType.YMD_CN_HMS,
        ]:
            time_format = self.format.value.replace("年", "Nian").replace("月", "Yue").replace("日", "Ri")
            datetime_current = self.time.strftime(time_format)
            return datetime_current.replace("Nian", "年").replace("Yue", "月").replace("Ri", "日")
        else:
            return self.time.strftime(self.format.value)

    def __repr__(self):
        return self.__str__()

    @typesMg.shortcut("Date", res_type="Str")
    def get_time_str(self) -> str:
        return self.__str__()

    @typesMg.shortcut("Date", res_type="Int")
    def get_time_year(self) -> int:
        return self.time.year

    @typesMg.shortcut("Date", res_type="Int")
    def get_time_month(self) -> int:
        return self.time.month

    @typesMg.shortcut("Date", res_type="Int")
    def get_time_day(self) -> int:
        return self.time.day

    @typesMg.shortcut("Date", res_type="Int")
    def get_time_hour(self) -> int:
        return self.time.hour

    @typesMg.shortcut("Date", res_type="Int")
    def get_time_minute(self) -> int:
        return self.time.minute

    @typesMg.shortcut("Date", res_type="Int")
    def get_time_second(self) -> int:
        return self.time.second

    @typesMg.shortcut("Date", res_type="Int")
    def get_time_weekday(self) -> int:
        return self.time.weekday() + 1

    @typesMg.shortcut("Date", res_type="Int")
    def get_time_week(self) -> int:
        return self.time.isocalendar()[1]


class URL(Str):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, URL):
            return value
        try:
            temp_value = str(value)
            temp_value = temp_value.strip()
            if len(temp_value) == 0:
                raise BaseException(
                    PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                    "{}参数验证失败".format(
                        name,
                    ),
                )
            if "://" not in temp_value:
                temp_value = "http://" + temp_value
            return cls(temp_value)
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class Pick(Dict):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, Pick):
            return value
        try:
            if not value:
                return None
            return cls(dict(value))
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class WebPick(Pick):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, WebPick):
            return value
        try:
            if not value:
                return None
            return cls(dict(value))
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class WinPick(Pick):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locator = None  # 如果包含locator就直接使用locator

    def __str__(self):
        if self.locator is not None:
            return self.locator.__str__()
        return super().__str__()

    def __repr__(self):
        if self.locator is not None:
            return self.locator.__repr__()
        return super().__repr__()

    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, WinPick):
            return value
        try:
            if not value:
                return None
            return cls(dict(value))
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class IMGPick(Pick):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locator = None  # 如果包含locator就直接使用locator

    def __str__(self):
        if self.locator is not None:
            return self.locator.__str__()
        return super().__str__()

    def __repr__(self):
        if self.locator is not None:
            return self.locator.__repr__()
        return super().__repr__()

    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, IMGPick):
            return value
        try:
            if not value:
                return None
            return cls(dict(value))
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class FeishuBaseInstance(Dict):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, FeishuBaseInstance):
            return value
        try:
            return cls(dict(value))
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class DialogResult(Str):
    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, DialogResult):
            return value
        try:
            temp_value = str(value)
            temp_value = temp_value.strip()
            return cls(temp_value)
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class Password(Str):
    """主要是给前端标记为密码 ***"""

    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, Password):
            return value
        try:
            temp_value = str(value)
            temp_value = temp_value.strip()
            return cls(temp_value)
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e


class Ciphertext:
    def __init__(self, s: str):
        self.str = s
        self.__key__ = None  # 解密密钥，如果为空就说明不需要解密，密文就是解密,加密类型aes, 使用__隐藏方法

    def set_key(self, key: str):
        self.__key__ = key

    def decrypt(self):
        if self.__key__ is None:
            return self.str

        from Crypto.Cipher import AES

        key_bytes = self.__key__.encode("utf-8")
        decoded = b64decode(self.str)
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        decrypted = cipher.decrypt(decoded)
        res = decrypted[: -decrypted[-1]] if decrypted else b""
        return res.decode("utf-8")

    def __str__(self):
        # 显示密文，不会显示解密数据
        return self.str.__str__()

    def __repr__(self):
        # 显示密文，不会显示解密数据
        return self.str.__repr__()

    @classmethod
    def __validate__(cls, name: str, value):
        if isinstance(value, Ciphertext):
            return value
        try:
            temp_value = str(value)
            temp_value = temp_value.strip()
            return cls(temp_value)
        except Exception as e:
            raise BaseException(
                PARAM_VERIFY_ERROR_FORMAT.format(name, value),
                "{}参数验证失败{}：{}".format(name, value, e),
            ) from e
