import base64
import hashlib

from Cryptodome.Cipher import AES

from rpaencrypt import Base64CodeType, EncryptCaseType, MD5bitsType, SHAType


class EncryptCore:
    @staticmethod
    def md5_encrypt(
        source_str: str,
        md5_method: MD5bitsType = MD5bitsType.MD5_32,
        case_method: EncryptCaseType = EncryptCaseType.LOWER,
    ):
        """md5加密"""
        m = hashlib.md5()
        m.update(source_str.encode("utf8"))

        str_md5 = ""
        if md5_method == MD5bitsType.MD5_32:  # 加密位数：32位
            str_md5 = m.hexdigest()
        elif md5_method == MD5bitsType.MD5_16:  # 加密位数：16位
            str_md5 = m.hexdigest()[8:-8]

        if str_md5:
            if case_method == EncryptCaseType.LOWER:  # 小写
                str_md5 = str_md5.lower()
            elif case_method == EncryptCaseType.UPPER:  # 大写
                str_md5 = str_md5.upper()
        return str_md5

    @staticmethod
    def sha_encrypt(
        source_str: str,
        sha_method: SHAType = SHAType.SHA1,
        case_method: EncryptCaseType = EncryptCaseType.LOWER,
    ):
        """sha加密"""
        if sha_method == SHAType.SHA1:
            sha = hashlib.sha1()
        elif sha_method == SHAType.SHA224:
            sha = hashlib.sha224()
        elif sha_method == SHAType.SHA256:
            sha = hashlib.sha256()
        elif sha_method == SHAType.SHA384:
            sha = hashlib.sha384()
        elif sha_method == SHAType.SHA512:
            sha = hashlib.sha512()
        elif sha_method == SHAType.SHA3_224:
            sha = hashlib.sha3_224()
        elif sha_method == SHAType.SHA3_256:
            sha = hashlib.sha3_256()
        elif sha_method == SHAType.SHA3_384:
            sha = hashlib.sha3_384()
        elif sha_method == SHAType.SHA3_512:
            sha = hashlib.sha3_512()

        sha.update(source_str.encode("utf8"))
        str_sha = sha.hexdigest()

        if case_method == EncryptCaseType.LOWER:  # 小写
            str_sha = str_sha.lower()
        elif case_method == EncryptCaseType.UPPER:  # 大写
            str_sha = str_sha.upper()

        return str_sha

    @staticmethod
    def symmetric_encrypt(source_str: str, password: str = ""):
        """AES对称加密"""

        # 需要补位，若str不是16的倍数，则补足为16的倍数
        def add_to_16(value):
            while len(value.encode("utf-8")) % 16 != 0:
                value += "\0"
            return value.encode("utf-8")

        if len(source_str) == 0:
            raise ValueError("加密对象不能为空!")

        if isinstance(source_str, str):
            password = str(password)
            iv = password  # 初始化偏移向量,偏移向量必须为16bit
            aes = AES.new(add_to_16(password), AES.MODE_CBC, add_to_16(iv))  # 初始化加密器
            encrypt_aes = aes.encrypt(add_to_16(source_str))  # 进行 aes 加密
            aes_encrypt = str(base64.b64encode(encrypt_aes), encoding="utf-8")  # 执行加密并转码返回 bytes
            return aes_encrypt
        else:
            raise ValueError("请提供字符串类型对象！")

    @staticmethod
    def symmetric_decrypt(source_str: str, password: str = ""):
        """AES对称解密"""

        # 需要补位，若str不是16的倍数，则补足为16的倍数
        def add_to_16(value):
            while len(value.encode("utf-8")) % 16 != 0:
                value += "\0"
            return value.encode("utf-8")

        if len(source_str) == 0:
            raise ValueError("解密对象不能为空!")

        if isinstance(source_str, str):
            password = str(password)
            iv = password  # 初始化偏移向量为密钥
            aes = AES.new(add_to_16(password), AES.MODE_CBC, add_to_16(iv))  # 初始化加密器
            base64_decrypted = base64.decodebytes(source_str.encode(encoding="utf-8"))  # 优先逆向解密 base64 成 bytes
            aes_decrypt = str(aes.decrypt(base64_decrypted), encoding="utf-8").replace(
                "\0", ""
            )  # 执行解密密并转码返回str
            return aes_decrypt
        else:
            raise ValueError("请提供字符串类型对象！")

    @staticmethod
    def base64_encode(
        encode_type: Base64CodeType = Base64CodeType.STRING,
        string_data: str = "",
        file_path: str = "",
    ) -> str:
        import base64

        if file_path:
            with open(file_path, "rb") as file:
                input_content = file.read()
        else:
            input_content = string_data.encode("utf-8")
        base64_encoded = base64.b64encode(input_content)
        base64_encode_result = base64_encoded.decode("utf-8")
        if encode_type == Base64CodeType.PICTURE:
            base64_encode_result = "data:image/png;base64," + base64_encode_result
        return base64_encode_result

    @staticmethod
    def base64_decode(
        decode_type: Base64CodeType = Base64CodeType.STRING,
        string_data: str = "",
        file_path: str = "",
    ):
        def add_to_4(value):
            while len(value) % 4 != 0:
                value += "="
            return value

        if decode_type == Base64CodeType.STRING:
            base64_decode_result = base64.b64decode(add_to_4(string_data))
            base64_decode_result = str(base64_decode_result, "utf-8")
            return base64_decode_result
        else:
            if file_path:
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(string_data.replace("data:image/png;base64,", "")))
            return file_path
