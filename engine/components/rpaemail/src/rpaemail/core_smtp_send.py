import ast
import copy
import mimetypes
import os
import smtplib
import time
from email.encoders import encode_base64
from email.header import Header, make_header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from typing import Union

from rpaemail.error import *
from rpaframe.logger.logger import logger


class EmailSmtpSend:
    def __init__(self):
        self.mail_handler = None

    def login(self, server, port: int, user, password, use_ssl: bool = False, timeout=20):
        if use_ssl:
            self.mail_handler = smtplib.SMTP_SSL(server, port, timeout=timeout)
        else:
            self.mail_handler = smtplib.SMTP(server, port, timeout=timeout)
        try:
            self.mail_handler.login(user, password)
        except smtplib.SMTPException as e:
            logger.error("login error: {}".format(e))
            return False
        return True

    @staticmethod
    def __handle_email_address__(address_list):
        address_group_list = []
        if isinstance(address_list, list):
            address_group_list = [
                list(filter(lambda a: a, email.replace("；", ";").split(";"))) for email in address_list
            ]
        elif isinstance(address_list, str):
            address_list = address_list.replace("；", ";")
            try:
                address_list = ast.literal_eval(address_list)
                address_group_list = [list(filter(lambda a: a, email.split(";"))) for email in address_list]
            except Exception as e:
                address_group_list = [list(filter(lambda a: a, address_list.split(";")))]
                address_list = [address_list]

        # address_list是装载了原本输入str的list ["a@qq.com;b@qq.com","a@163.com]
        # address_group_list是装在了分号分开后的list的list [["a@qq,com","b@qq.com"],["a@163.com"]]
        return address_list, address_group_list

    @staticmethod
    def __handle_attachment__(attachment_path):
        """
        添加附件. 后面需要添加多个附件，可以外部循环调用此方法.
        """
        attachment_filename = os.path.basename(attachment_path)
        data = open(attachment_path, "rb")
        ctype, encoding = mimetypes.guess_type(attachment_path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        file_msg = MIMEBase(maintype, subtype)
        file_msg.set_payload(data.read())
        file_msg.add_header(
            "Content-Disposition",
            "attachment",
            filename=(make_header([(attachment_filename, "UTF-8")]).encode("UTF-8")),
        )
        data.close()
        encode_base64(file_msg)  # 把附件编码
        return file_msg

    def send(
        self,
        user,
        user_name,
        receiver: Union[str, list] = "",
        cc: Union[str, list] = "",
        bcc: Union[str, list] = "",
        content: str = "",
        content_is_html: bool = False,
        subject: str = "",
        attachment_path: str = "",
    ):
        receiver_list, receiver_group_list = self.__handle_email_address__(receiver)
        if not receiver_list:
            return False

        cc_list, cc_group_list = self.__handle_email_address__(cc)
        if len(cc_list) == 1:
            cc_list = [cc_list[0]] * len(receiver_list)
            cc_group_list = [cc_group_list[0]] * len(receiver_list)

        bcc_list, bcc_group_list = self.__handle_email_address__(bcc)
        if len(bcc_list) == 1:
            bcc_list = [bcc_list[0]] * len(receiver_list)
            bcc_group_list = [bcc_group_list[0]] * len(receiver_list)

        origin_content = copy.deepcopy(content)

        for i in range(len(receiver_list)):
            msg = MIMEMultipart()
            name, addr = parseaddr(f"{user_name} <{user}>")
            msg["From"] = formataddr((Header(name, "utf-8").encode(), addr))
            msg["To"] = Header(receiver_list[i])
            msg["Cc"] = cc_list[i]
            msg["Bcc"] = bcc_list[i]
            msg["date"] = time.strftime("%a, %d %b %Y %H:%M:%S %z")
            msg["Subject"] = subject if subject else "来自{}的邮件".format(user)
            if not content_is_html:
                msg.attach(MIMEText(origin_content, "plain", "utf-8"))
            else:
                msg.attach(MIMEText(origin_content, "html", "utf-8"))
            if attachment_path:
                for item_path in attachment_path.split(","):
                    if item_path:
                        msg.attach(self.__handle_attachment__(item_path))

            try:
                self.mail_handler.sendmail(
                    user,
                    receiver_group_list[i] + cc_group_list[i] + bcc_group_list[i],
                    msg.as_string(),
                )
            except smtplib.SMTPException as e:
                raise BaseException(LOGIN_FAIL_FORMAT.format(e), "发送失败{}".format(e))
