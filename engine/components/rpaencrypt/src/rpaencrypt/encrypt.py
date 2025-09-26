import os

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaatomic.utils import FileExistenceType, handle_existence

from rpaencrypt import Base64CodeType, EncryptCaseType, MD5bitsType, SHAType
from rpaencrypt.core import EncryptCore


class Encrypt:
    @staticmethod
    @atomicMg.atomic("Encrypt", outputList=[atomicMg.param("md5_encrypted_result", types="Str")])
    def md5_encrypt(
        source_str: str,
        md5_method: MD5bitsType = MD5bitsType.MD5_32,
        case_method: EncryptCaseType = EncryptCaseType.LOWER,
    ) -> str:
        """
        MD5加密算法
        """
        if source_str:
            md5_encrypted_result = EncryptCore.md5_encrypt(source_str, md5_method, case_method)
            return md5_encrypted_result

    @staticmethod
    @atomicMg.atomic("Encrypt", outputList=[atomicMg.param("sha_encrypted_result", types="Str")])
    def sha_encrypt(
        source_str: str,
        sha_method: SHAType = SHAType.SHA1,
        case_method: EncryptCaseType = EncryptCaseType.LOWER,
    ) -> str:
        """
        SHA加密算法
        """
        if source_str:
            sha_encrypted_result = EncryptCore.sha_encrypt(source_str, sha_method, case_method)
            return sha_encrypted_result

    @staticmethod
    @atomicMg.atomic(
        "Encrypt",
        outputList=[atomicMg.param("symmetric_encrypted_result", types="Str")],
    )
    def symmetric_encrypt(source_str: str, password: str = "") -> str:
        """
        对称加密算法
        """
        if source_str:
            symmetric_encrypted_result = EncryptCore.symmetric_encrypt(source_str, password)
            return symmetric_encrypted_result

    @staticmethod
    @atomicMg.atomic(
        "Encrypt",
        outputList=[atomicMg.param("symmetric_decrypted_result", types="Str")],
    )
    def symmetric_decrypt(source_str: str, password: str = "") -> str:
        """
        对称解密算法
        """
        if source_str:
            symmetric_decrypted_result = EncryptCore.symmetric_decrypt(source_str, password)
            return symmetric_decrypted_result

    # --------------Base64操作-----------------
    @staticmethod
    @atomicMg.atomic(
        "Encrypt",
        inputList=[
            atomicMg.param(
                "string_data",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.string_data.show",
                        expression="return $this.encode_type.value == '{}'".format(Base64CodeType.STRING.value),
                    )
                ],
            ),
            atomicMg.param(
                "file_path",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.encode_type.value == '{}'".format(Base64CodeType.PICTURE.value),
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
        ],
        outputList=[atomicMg.param("encoded_string", types="Str")],
    )
    def base64_encoding(
        encode_type: Base64CodeType = Base64CodeType.STRING,
        string_data: str = "",
        file_path: str = "",
    ):
        if encode_type == Base64CodeType.PICTURE and not os.path.exists(file_path):
            raise ValueError("图片文件不存在!")
        encoded_string = EncryptCore.base64_encode(encode_type, string_data, file_path)
        return encoded_string

    @staticmethod
    @atomicMg.atomic(
        "Encrypt",
        inputList=[
            atomicMg.param(
                "file_path",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_path.show",
                        expression="return $this.decode_type.value == '{}'".format(Base64CodeType.PICTURE.value),
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "folder"},
                ),
            ),
            atomicMg.param(
                "file_name",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.file_name.show",
                        expression="return $this.decode_type.value == '{}'".format(Base64CodeType.PICTURE.value),
                    )
                ],
            ),
            atomicMg.param(
                "exist_handle_type",
                level=AtomicLevel.ADVANCED,
                dynamics=[
                    DynamicsItem(
                        key="$this.exist_handle_type.show",
                        expression="return $this.decode_type.value == '{}'".format(Base64CodeType.PICTURE.value),
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("decoded_string", types="Str")],
    )
    def base64_decoding(
        decode_type: Base64CodeType = Base64CodeType.STRING,
        string_data: str = "",
        file_path: str = "",
        file_name: str = "",
        exist_handle_type: FileExistenceType = FileExistenceType.RENAME,
    ):
        new_file_path = os.path.join(file_path, file_name + ".png") if decode_type == Base64CodeType.PICTURE else ""
        if new_file_path:
            new_file_path = handle_existence(new_file_path, exist_handle_type)
        decoded_string = EncryptCore.base64_decode(decode_type, string_data, new_file_path)
        return decoded_string
