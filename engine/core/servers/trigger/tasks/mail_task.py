import email
import imaplib
import poplib
from datetime import datetime
from email.header import Header
from email.utils import parseaddr

from apscheduler.triggers.interval import IntervalTrigger

from ..core.logger import logger

global_mail_ids = {}

CONDITION_OR = "or"
CONDITION_AND = "and"
CONDITION_ALL = "all"


def decode_data(bytes, added_encode=None):
    """
    字节解码
    :param bytes:
    :return:
    """

    def _decode(bytes, encoding):
        try:
            return str(bytes, encoding=encoding)
        except Exception as e:
            return None

    encodes = ["GB2312", "UTF-8", "GBK"]
    if added_encode:
        encodes = [added_encode] + encodes
    for encoding in encodes:
        str_data = _decode(bytes, encoding)
        if str_data is not None:
            return str_data
    return None


class MailTask:
    def __init__(
        self,
        task_id: str,
        end_time: str = None,
        sender_text: str = None,
        receiver_text: str = None,
        theme_text: str = None,
        content_text: str = None,
        interval_time: int = 1,
        condition: str = "or",
        attachment: bool = False,
        **kwargs,
    ):
        """
        构建邮箱检查的类

        task_id: `str`, 任务id
        end_time: `str`, 是否启用结束时间
        sender_text: `str`, 通过发送者包含关键字进行过滤
        receiver_text: `str`, 通过接收者包含关键字进行过滤
        theme_text: `str`, 通过主题包含关键字进行过滤
        content_text: `str`, 通过内容包含关键字进行过滤
        interval_time: `int`, 检查邮件的间隔时间
        condition: `str`, 邮箱过滤条件的组合判断
        attachment: `bool`, 邮箱过滤是否有附件
        Kwargs: 该参数用于构建任务的详细参数状态
            - mail_flag: 三方邮箱厂商的不同类型，支持传入`163`、`126`、`qq`、`iflytek`、`advance`
            - custom_mail_server: 用户自定义邮箱服务地址
            - custom_mail_port: 用户自定义邮箱端口
            - user_mail: 用户邮箱账号
            - user_authorization: 用户邮箱授权码

        """

        self.sender_text: str = sender_text
        self.receiver_text: str = receiver_text
        self.theme_text: str = theme_text
        self.content_text: str = content_text
        self.task_id: str = task_id
        self._end_time: str = end_time
        self.interval_time: int = interval_time
        self.condition = condition
        self.attachment = attachment

        self.mail_flag: str = kwargs.get("mail_flag")
        self.custom_mail_server: str = kwargs.get("custom_mail_server")
        self.custom_mail_port: str = kwargs.get("custom_mail_port", "993")
        self.custom_mail_protocol: str = kwargs.get("custom_mail_protocol", "IMAP")
        self.custom_mail_ssl: bool = kwargs.get("custom_mail_ssl", True)
        self.user_mail: str = kwargs.get("user_mail")
        self.user_authorization: str = kwargs.get("user_authorization")

        self.mail_server_dict = {
            # IMAP SSL
            "qq": ["imap.qq.com", 993, "IMAP", True],
            "163": ["imap.163.com", 993, "IMAP", True],
            "126": ["imap.126.com", 993, "IMAP", True],
            "iflytek": ["mail.iflytek.com", 993, "IMAP", True],
            # 自定义配置
            "advance": [
                self.custom_mail_server,
                self.custom_mail_port,
                self.custom_mail_protocol,
                self.custom_mail_ssl,
            ],
        }

    def connect(self):
        """
        同步方法，提供给外部进行邮箱连接可用性检测
        :param host:
        :param port:
        :param user_mail:
        :param user_authorization:
        :return:
        """
        try:
            used_mail_server, used_mail_port, used_mail_protocol, used_mail_ssl = self.mail_server_dict[self.mail_flag]

            # 根据协议和SSL设置创建相应的客户端
            if used_mail_protocol == "IMAP":
                if used_mail_ssl:
                    client = imaplib.IMAP4_SSL(host=used_mail_server, port=int(used_mail_port))
                else:
                    client = imaplib.IMAP4(host=used_mail_server, port=int(used_mail_port))

                client.login(self.user_mail, self.user_authorization)
                client.logout()  # 登出
                return True
            elif used_mail_protocol == "POP3":
                if used_mail_ssl:
                    client = poplib.POP3_SSL(host=used_mail_server, port=int(used_mail_port))
                else:
                    client = poplib.POP3(host=used_mail_server, port=int(used_mail_port))

                client.user(self.user_mail)
                client.pass_(self.user_authorization)
                client.quit()  # 退出
                return True
            else:
                raise ValueError(f"不支持的邮件协议: {used_mail_protocol}")
        except Exception as e:
            return False

    async def aconnect(self):
        """
        异步方法，连接邮箱客户端并返回
        :return:
        """
        try:
            used_mail_server, used_mail_port, used_mail_protocol, used_mail_ssl = self.mail_server_dict[self.mail_flag]

            # 统一使用同步方式，在异步函数中运行
            if used_mail_protocol == "IMAP":
                if used_mail_ssl:
                    client = imaplib.IMAP4_SSL(host=used_mail_server, port=int(used_mail_port))
                else:
                    client = imaplib.IMAP4(host=used_mail_server, port=int(used_mail_port))

                # 登录
                client.login(self.user_mail, self.user_authorization)
                imaplib.Commands["ID"] = "AUTH"
                args = (
                    "name",
                    self.user_mail.split("@")[0],
                    "contact",
                    self.user_mail,
                    "version",
                    "1.0.0",
                    "vendor",
                    "myclient",
                )
                client._simple_command("ID", '("' + '" "'.join(args) + '")')
                logger.info(f"【AsyncMailTask callback】IMAP登录成功")

                return client
            elif used_mail_protocol == "POP3":
                if used_mail_ssl:
                    client = poplib.POP3_SSL(host=used_mail_server, port=int(used_mail_port))
                else:
                    client = poplib.POP3(host=used_mail_server, port=int(used_mail_port))

                client.user(self.user_mail)
                client.pass_(self.user_authorization)
                logger.info(f"【AsyncMailTask callback】POP3登录成功")

                return client
            else:
                raise ValueError(f"不支持的邮件协议: {used_mail_protocol}")

        except Exception as e:
            logger.info(f"【AsyncMailTask callback】连接邮箱时报错：{str(e)}")
            import traceback

            logger.info(f"【AsyncMailTask callback】详细错误信息：{traceback.format_exc()}")
            return None

    async def search_all(self, client, condition: str = "ALL"):
        """搜索邮件"""
        # 根据协议类型处理
        if self.custom_mail_protocol == "IMAP":
            # IMAP协议 - 需要先选择邮箱，再搜索
            try:
                # 先选择INBOX
                status, data = client.select("INBOX")
                if status != "OK":
                    logger.error(f"【AsyncMailTask callback】选择INBOX失败：{status} - {data}")
                    return False

                # 然后搜索邮件
                status, data = client.search(None, condition)
                if status != "OK":
                    logger.error(f"【AsyncMailTask callback】搜索邮件失败：{status} - {data}")
                    return False
                return data
            except Exception as e:
                logger.error(f"【AsyncMailTask callback】IMAP搜索邮件异常：{str(e)}")
                return False
        elif self.custom_mail_protocol == "POP3":
            # POP3协议 - 获取所有邮件数量
            try:
                num_messages = len(client.list()[1])
                # 返回邮件ID列表（POP3使用数字ID）
                return [str(i + 1).encode() for i in range(num_messages)]
            except Exception as e:
                logger.info(f"【AsyncMailTask callback】POP3获取邮件列表失败：{str(e)}")
                return False
        else:
            logger.error(f"【AsyncMailTask callback】不支持的协议：{self.custom_mail_protocol}")
            return False

    async def callback(self) -> bool:
        """
        检查回调

        :return
            `bool`, 标识是否调度成功
        """

        # 邮箱连接
        logger.info("【AsyncMailTask callback】准备开始连接邮箱...")
        try:
            client = await self.aconnect()
            if not client:
                logger.error("【AsyncMailTask callback】邮箱Client链接失败")
                return False
        except Exception as e:
            logger.error(f"【AsyncMailTask callback】连接邮箱异常：{str(e)}")
            return False

        # 查询当前邮筒的所有邮件（search_all会自动选择INBOX）
        try:
            data = await self.search_all(client)
            if not data:
                logger.info("【AsyncMailTask callback】获取邮件列表失败")
                return False
        except Exception as e:
            logger.error(f"【AsyncMailTask callback】搜索邮件异常：{str(e)}")
            return False

        # 处理邮件ID列表
        if self.custom_mail_protocol == "IMAP":
            # if len(data) > 1 and data[1] == b'SEARCH completed':
            #     # IMAP返回格式：(b'1 2 3 4 5...', b'SEARCH completed')
            #     email_ids = data[0].split()
            # else:
            email_ids = data[0].split()
        elif self.custom_mail_protocol == "POP3":
            # POP3返回的是列表
            email_ids = data

        cache_ids = global_mail_ids.get(self.task_id, [])
        logger.info(f"【AsyncMailTask callback】获取邮筒当前邮件成功：{len(email_ids)} 封邮件")

        # 智能处理大量邮件：只检查新增的邮件
        if not cache_ids:
            cache_ids = email_ids
            global_mail_ids[self.task_id] = cache_ids
            return False  # 首次运行不触发，只建立基准

        # 判断邮件序列是否新增
        if len(cache_ids) >= len(email_ids):
            # 邮件数量没有增加，更新缓存为最新的邮件ID
            global_mail_ids[self.task_id] = email_ids
            return False

        # 计算新增的邮件数量
        distance = len(email_ids) - len(cache_ids)
        if distance > 0:
            # 只检查新增的邮件
            updated_ids = email_ids[-distance:]
            logger.info(f"【AsyncMailTask callback】发现{distance}封新邮件，开始检查")
        else:
            # 邮件数量没有变化，但可能邮件ID有变化（邮件被删除等）
            global_mail_ids[self.task_id] = email_ids
            return False
        # 如果有过滤条件，则逐封判断
        logger.info(f"【AsyncMailTask callback】准备开始进行循环判断新邮件...")
        processed_count = 0
        for email_id in updated_ids:
            try:
                # 根据协议类型获取邮件内容
                if self.custom_mail_protocol == "IMAP":
                    # IMAP协议
                    status, data = client.fetch(email_id.decode(), "RFC822")
                elif self.custom_mail_protocol == "POP3":
                    # POP3协议
                    email_id_str = email_id.decode() if isinstance(email_id, bytes) else str(email_id)
                    data = client.retr(int(email_id_str))
                    # POP3返回的是元组 (response, lines, octets)
                    data = [data[1]]  # 转换为与IMAP相同的格式
                else:
                    logger.error(f"【AsyncMailTask callback】不支持的协议：{self.custom_mail_protocol}")
                    continue

                mail_info = self._extract_info(data, self.custom_mail_protocol)
                processed_count += 1
                logger.info(f"【AsyncMailTask callback】已读取邮件信息完毕，准备开始判断：{mail_info}...")

                if self._check_mail_conditions(mail_info):
                    logger.info(f"【AsyncMailTask callback】进入条件{self.condition}")
                    global_mail_ids[self.task_id] = email_ids
                    return True

            except Exception as e:
                logger.error(f"【AsyncMailTask callback】读取邮件失败：{str(e)}")
                continue

        logger.info(f"【AsyncMailTask callback】处理了 {processed_count} 封新邮件，没有符合的邮件信息，直接返回")
        global_mail_ids[self.task_id] = email_ids
        return False

    def _check_mail_conditions(self, mail_info):
        """
        检查邮件是否符合过滤条件

        Args:
            mail_info: 邮件信息字典

        Returns:
            bool: 是否符合条件
        """
        # 收集所有非空条件的匹配结果
        conditions = []

        if self.sender_text:  # 只有非空条件才参与判断
            sender_match = self._check_sender(mail_info)
            conditions.append(("sender", sender_match))

        if self.receiver_text:
            receiver_match = self._check_receiver(mail_info)
            conditions.append(("receiver", receiver_match))

        if self.theme_text:
            subject_match = self._check_subject(mail_info)
            conditions.append(("subject", subject_match))

        if self.content_text:
            content_match = self._check_content(mail_info)
            conditions.append(("content", content_match))

        if self.attachment is not None:  # 附件条件特殊处理，None表示不限制
            attachment_match = self._check_attachment(mail_info)
            conditions.append(("attachment", attachment_match))

        # 记录匹配结果
        condition_logs = [f"{name}: {match}" for name, match in conditions]
        logger.info(f"【AsyncMailTask callback】条件匹配结果: {', '.join(condition_logs)}")

        # 如果没有设置任何条件，返回True
        if not conditions:
            return True

        # 根据条件类型进行判断
        if self.condition == CONDITION_OR:
            # OR条件：任一条件满足即可
            return any(match for _, match in conditions)
        elif self.condition == CONDITION_AND:
            # AND条件：所有条件都必须满足
            return all(match for _, match in conditions)
        elif self.condition == CONDITION_ALL:
            # ALL条件：无条件匹配
            return True
        else:
            return False

    def _check_sender(self, mail_info):
        """检查发件人是否匹配"""
        if not mail_info.get("from"):
            return False
        sender_text = " ".join([item for item in mail_info["from"] if item])
        return self.sender_text in sender_text

    def _check_receiver(self, mail_info):
        """检查收件人是否匹配"""
        if not mail_info.get("to"):
            return False
        receiver_text = " ".join([item for item in mail_info["to"] if item])
        return self.receiver_text in receiver_text

    def _check_subject(self, mail_info):
        """检查主题是否匹配"""
        if not mail_info.get("subject"):
            return False
        return self.theme_text in mail_info["subject"]

    def _check_content(self, mail_info):
        """检查内容是否匹配"""
        if not mail_info.get("body"):
            return False
        return self.content_text in mail_info["body"]

    def _check_attachment(self, mail_info):
        """检查附件条件是否匹配"""
        return self.attachment == mail_info.get("has_attachment", False)

    @staticmethod
    def _extract_info(data, mail_type="IMAP"):
        """
        返回邮件的解析后信息部分
        返回列表包含（主题，纯文本正文部分，html的正文部分，发件人元组，收件人元组，附件列表）

        """

        def get_sender_info(msg):
            name = email.utils.parseaddr(msg["from"])[0]
            deName = email.header.decode_header(name)[0]
            if deName[1] != None:
                name = decode_data(deName[0], deName[1])
                # name = deName[0].decode(deName[1])
            address = email.utils.parseaddr(msg["from"])[1]
            return (name, address)

        def get_receiver_info(msg):
            name = email.utils.parseaddr(msg["to"])[0]
            deName = email.header.decode_header(name)[0]
            if deName[1] != None:
                name = decode_data(deName[0], deName[1])
                # name = deName[0].decode(deName[1])
            address = email.utils.parseaddr(msg["to"])[1]
            return (name, address)

        def get_subject_content(msg):
            try:
                deContent = email.header.decode_header(msg["subject"])[0]
            except:
                return msg["subject"]

            if deContent[1] != None:
                return decode_data(deContent[0], deContent[1])
            return deContent[0]

        def get_mail_time(msg):
            date_tuple = email.utils.parsedate_tz(msg["Date"])
            if date_tuple:
                local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                formatted_time = local_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                formatted_time = None
            return formatted_time

        body = None
        html = None
        has_attachment = False

        # 处理不同协议的数据格式
        if mail_type == "IMAP":
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], tuple):
                    # IMAP格式：data[0] = (b'1 (RFC822 {1234}', b'...邮件内容...')
                    msg = email.message_from_string(decode_data(data[0][1]))
                elif isinstance(data[1], (bytes, bytearray)) and len(data) > 1:
                    # IMAP异步fetch格式：data[1] = bytearray(b'...邮件内容...')
                    msg = email.message_from_string(decode_data(data[1]))
        if mail_type == "POP3":
            # POP3格式：data[0] = [b'...邮件内容行1...', b'...邮件内容行2...', ...]
            # 需要将多行合并成一个字符串
            email_content = b"\n".join(data[0])
            msg = email.message_from_string(decode_data(email_content))

        logger.info(f"【AsyncMailTask callback】邮件信息：{msg}")

        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                if body is None:
                    body = b""
                body += part.get_payload(decode=True)
            elif part.get_content_type() == "text/html":
                if html is None:
                    html = b""
                html += part.get_payload(decode=True)

            if not has_attachment:
                name = part.get_filename()
                if name:
                    has_attachment = True

        return {
            "from": get_sender_info(msg),  # 发送人
            "to": get_receiver_info(msg),  # 接收人
            "subject": get_subject_content(msg),  # 主题
            "body": decode_data(body),  # 文字内容
            "html": decode_data(html),  # （正文）html信息
            "time": get_mail_time(msg),  # 发送时间
            "has_attachment": has_attachment,  # 是否包含附件
        }

    def to_trigger(self):
        """获取该类任务的触发器模型"""
        return IntervalTrigger(end_date=self._end_time, **{"minutes": self.interval_time})
