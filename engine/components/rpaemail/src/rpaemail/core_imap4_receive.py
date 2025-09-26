import email
import imaplib
from datetime import datetime


def decode_data(b, added_encode=None):
    """
    字节解码
    """

    def _decode(bs, encoding):
        try:
            return str(bs, encoding=encoding)
        except Exception as e:
            return None

    encodes = ["GB2312", "UTF-8", "GBK"]
    if added_encode:
        encodes = [added_encode] + encodes
    for encoding in encodes:
        str_data = _decode(b, encoding)
        if str_data is not None:
            return str_data
    return None


class EmailImap4Receive:
    def __init__(self):
        self.mail_handler = None

    def login(self, server, port: int, user, password):
        self.mail_handler = imaplib.IMAP4_SSL(server, port)
        self.mail_handler.login(user, password)
        self.__build_header__(user)

    def __build_header__(self, user):
        """
        构建网易客户端id
        """
        imaplib.Commands["ID"] = "AUTH"
        args = (
            "name",
            user.split("@")[0],
            "contact",
            user,
            "version",
            "1.0.0",
            "vendor",
            "myclient",
        )
        self.mail_handler._simple_command("ID", '("' + '" "'.join(args) + '")')

    def showFolders(self):
        """
        返回所有文件夹

        """
        return self.mail_handler.list()

    def select(self, selector):
        """
        选择收件箱（如“INBOX”，如果不知道可以调用showFolders）
        """
        return self.mail_handler.select(selector)

    def search(self, charset="utf-8", *criteria):
        """
        查找邮件 搜索邮件(参照RFC文档http://tools.ietf.org/html/rfc3501#page-49)

        :param charset:
        :param criteria:
            1. support `FROM`、`TO`、`BODY`、`SUBJECT` to filter by keyword
            2. support `Unseen`、`All`、`Seen`、`(SINCE "01-Jan-2017")` to filter by mail's state
        :return:
        """
        try:
            return self.mail_handler.search(charset, *criteria)
        except Exception as e:
            self.select("INBOX")
            return self.mail_handler.search(charset, *criteria)

    def __get_email_format__(self, num):
        """
        以RFC822协议格式返回邮件详情的email对象

        :param num:
        :return: msg
        """
        data = self.mail_handler.fetch(num, "RFC822")
        if data[0] == "OK":
            return email.message_from_string(decode_data(data[1][0][1]))
        else:
            return "fetch error"

    @staticmethod
    def __parse_attachment__(message_part):
        content_disposition = message_part.get("Content-Disposition", None)
        if not content_disposition:
            return None

        dispositions = content_disposition.strip().split(";")
        if not bool(content_disposition and dispositions[0].lower() == "attachment"):
            return None

        attachment = {}
        file_data = message_part.get_payload(decode=True)
        attachment["content_type"] = message_part.get_content_type()
        attachment["size"] = len(file_data) if file_data else None
        de_name = email.header.decode_header(message_part.get_filename())[0]
        name = de_name[0]
        if de_name[1] is not None:
            name = de_name[0].decode(de_name[1])
        attachment["name"] = name
        attachment["data"] = file_data
        return attachment

    @staticmethod
    def __get_sender_info__(msg):
        """返回发送者的信息——元组（邮件称呼，邮件地址）"""
        name = email.utils.parseaddr(msg["from"])[0]
        de_name = email.header.decode_header(name)[0]
        if de_name[1] is not None:
            name = decode_data(de_name[0], de_name[1])
        address = email.utils.parseaddr(msg["from"])[1]
        return name, address

    @staticmethod
    def __get_receiver_info__(msg):
        """返回接受者的信息——元组（邮件称呼，邮件地址）"""
        name = email.utils.parseaddr(msg["to"])[0]
        de_name = email.header.decode_header(name)[0]
        if de_name[1] is not None:
            name = decode_data(de_name[0], de_name[1])
        address = email.utils.parseaddr(msg["to"])[1]
        return name, address

    @staticmethod
    def __get_subject_content__(msg):
        """返回邮件的主题（参数msg是email对象，可调用getEmailFormat获得）"""
        try:
            de_content = email.header.decode_header(msg["subject"])[0]
        except Exception as e:
            return msg["subject"]
        if de_content[1] is not None:
            return decode_data(de_content[0], de_content[1])
        return de_content[0]

    @staticmethod
    def __get_email_time__(msg):
        date_tuple = email.utils.parsedate_tz(msg["Date"])
        if date_tuple:
            local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            formatted_time = local_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            formatted_time = None
        return formatted_time

    def get_entire_mail_info(self, num):
        """
        返回邮件的解析后信息部分
        返回列表包含（主题，纯文本正文部分，html的正文部分，发件人元组，收件人元组，附件列表）
        """
        msg = self.__get_email_format__(num)
        attachments = []
        body = None
        html = None

        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                if body is None:
                    body = b""
                body += part.get_payload(decode=True)
            elif part.get_content_type() == "text/html":
                if html is None:
                    html = b""
                html += part.get_payload(decode=True)
            else:
                attachment = self.__parse_attachment__(part)
                attachments.append(attachment)
        return {
            "from": self.__get_sender_info__(msg),
            "to": self.__get_receiver_info__(msg),
            "subject": self.__get_subject_content__(msg),
            "body": decode_data(body),
            "html": decode_data(html),
            "time": self.__get_email_time__(msg),
            "attachments": attachments,
        }

    def mask_as_read(self, num):
        """需要标注为已读"""
        self.mail_handler.store(num, "+FLAGS", "\\Seen")
