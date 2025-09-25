import copy
import os

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, AtomicLevel, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaemail import EmailSeenType, EmailServerType
from rpaframe.logger.logger import logger


class Email:
    @staticmethod
    @atomicMg.atomic(
        "Email",
        inputList=[
            atomicMg.param("cc", required=False),
            atomicMg.param(
                "content",
                required=False,
                formType=AtomicFormTypeMeta(type=AtomicFormType.CONTENTPASTE.value),
            ),
            atomicMg.param(
                "attachment_path",
                required=False,
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "files"},
                ),
            ),
            atomicMg.param("bcc", required=False),
            atomicMg.param(
                "replace_table",
                required=False,
                formType=AtomicFormTypeMeta(type=AtomicFormType.MODALBUTTON.value),
                need_parse="json_str",
            ),
            atomicMg.param("send_name", required=False),
            atomicMg.param(
                "other_mail_server",
                dynamics=[
                    DynamicsItem(
                        key="$this.other_mail_server.show",
                        expression="return $this.mail_server.value == '{}'".format(EmailServerType.OTHER.value),
                    )
                ],
                required=False,
            ),
            atomicMg.param("mail_port", required=False),
        ],
        outputList=[],
    )
    def send_email(
        receiver: str = "",
        cc: str = "",
        subject: str = "",
        is_html: bool = False,
        content: str = "",
        attachment_path: str = "",
        mail_server: EmailServerType = EmailServerType.QQ,
        other_mail_server: str = "",
        mail_port: int = 465,
        use_ssl: bool = True,
        sender_mail: str = "",
        send_name: str = "",
        password: str = "",
        bcc: str = "",
        replace_table: str = "",
    ):
        mail_server_dict = {
            EmailServerType.QQ: "smtp.qq.com",
            EmailServerType.NETEASE_163: "smtp.163.com",
            EmailServerType.NETEASE_126: "smtp.126.com",
            EmailServerType.IFLYTEK: "mail.iflytek.com",
            EmailServerType.OTHER: other_mail_server,
        }
        from rpaemail.core_smtp_send import EmailSmtpSend

        core = EmailSmtpSend()
        core.login(
            server=mail_server_dict.get(mail_server),
            port=mail_port,
            user=sender_mail,
            password=password,
            use_ssl=use_ssl,
        )

        # 替换逻辑
        content = copy.deepcopy(content)
        try:
            if replace_table and isinstance(replace_table, list):
                for replace in replace_table:
                    content = content.replace(str(replace.get("origintext")), str(replace.get("replacetext")))
        except Exception as e:
            pass
        core.send(
            user=sender_mail,
            user_name=send_name,
            receiver=receiver,
            cc=cc,
            bcc=bcc,
            content=content,
            content_is_html=is_html,
            subject=subject,
            attachment_path=attachment_path,
        )

    @staticmethod
    @atomicMg.atomic(
        "Email",
        inputList=[
            atomicMg.param(
                key="custom_mail_server",
                level=AtomicLevel.NORMAL,
                dynamics=[
                    DynamicsItem(
                        key="$this.custom_mail_server.show",
                        expression="return $this.mail_server.value == '{}'".format(EmailServerType.OTHER.value),
                    )
                ],
                types="Str",
            ),
            atomicMg.param(
                key="custom_mail_port",
                level=AtomicLevel.NORMAL,
                dynamics=[
                    DynamicsItem(
                        key="$this.custom_mail_port.show",
                        expression="return $this.mail_server.value == '{}'".format(EmailServerType.OTHER.value),
                    )
                ],
                types="Str",
            ),
            atomicMg.param("user_mail", level=AtomicLevel.NORMAL, types="Str", required=True),
            atomicMg.param("user_password", level=AtomicLevel.NORMAL, types="Str", required=True),
            atomicMg.param(
                "unseen_flag",
                formType=AtomicFormTypeMeta(type=AtomicFormType.CHECKBOX.value),
                level=AtomicLevel.NORMAL,
                required=True,
            ),
            atomicMg.param(
                "save_attachment_flag",
                formType=AtomicFormTypeMeta(type=AtomicFormType.CHECKBOX.value),
                level=AtomicLevel.NORMAL,
                required=True,
            ),
            atomicMg.param(
                key="save_attachment_path",
                level=AtomicLevel.NORMAL,
                dynamics=[
                    DynamicsItem(
                        key="$this.save_attachment_path.show",
                        expression="return $this.save_attachment_flag.value == true",
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "files"},
                ),
                types="Str",
            ),
            atomicMg.param("folder_name", types="Str", required=True),
            atomicMg.param(
                "mask_as_read_flag",
                formType=AtomicFormTypeMeta(type=AtomicFormType.CHECKBOX.value),
                required=True,
            ),
            atomicMg.param("sender_text", required=False, types="Str"),
            atomicMg.param("receiver_text", required=False, types="Str"),
            atomicMg.param("theme_text", required=False, types="Str"),
            atomicMg.param("content_text", required=False, types="Str"),
        ],
        outputList=[atomicMg.param("mail_list", types="Dict")],
    )
    def receive_email(
        mail_server: EmailServerType = EmailServerType.QQ,
        custom_mail_server: str = "",
        custom_mail_port: int = 993,
        user_mail: str = "",
        user_password: str = "",
        max_return_num: int = 5,
        unseen_flag: bool = False,
        save_attachment_flag: bool = False,
        save_attachment_path: str = "",
        folder_name: str = "INBOX",
        mask_as_read_flag: bool = False,
        sender_text: str = "",
        receiver_text: str = "",
        theme_text: str = "",
        content_text: str = "",
    ):
        """
        邮件接收原子能力
        user_mail: `str`, 用户地址信息
        user_password: `str`, 用户密码信息
        custom_mail_server: `str`, 用户输入三方厂商地址
        custom_mail_port: `int`, 用户输入端口
        folder_name: `str`，邮件目录
        mail_server: `EmailServerType`, 激活的厂商服务器类型

        max_return_num: `int`, 邮件最大返回数量
        sender_text: `str`, 通过发送者包含关键字进行过滤
        receiver_text: `str`, 通过接收者包含关键字进行过滤
        theme_text: `str`, 通过主题包含关键字进行过滤
        content_text: `str`, 通过内容包含关键字进行过滤

        save_attachment_flag: `bool`, 是否保存附件
        save_attachment_path: `str`, 附件保存路径
        unseen_flag: `str`, 是否仅操作未读邮件
        mask_as_read_flag: `bool`, 是否将操作过的邮件标记为已读
        """
        # 初始化参数
        if max_return_num == 0:
            return []

        mail_server_dict = {
            EmailServerType.QQ.value: "imap.qq.com",
            EmailServerType.NETEASE_163.value: "imap.163.com",
            EmailServerType.NETEASE_126.value: "imap.126.com",
            EmailServerType.IFLYTEK.value: "mail.iflytek.com",
            EmailServerType.OTHER.value: custom_mail_server,
        }
        from rpaemail.core_imap4_receive import EmailImap4Receive

        core = EmailImap4Receive()
        core.login(
            server=mail_server_dict.get(mail_server.value),
            port=custom_mail_port,
            user=user_mail,
            password=user_password,
            use_ssl=True,
        )
        core.select(selector=folder_name)

        mail_ids = []
        for num in core.search(
            "utf-8",
            EmailSeenType.ALL.value if not unseen_flag else EmailSeenType.UNSEEN.value,
        )[1][0].split(b" "):
            if not num or num == b"":
                continue
            try:
                logger.info(f"mail id:{str(num)}")
                mail_info = core.get_entire_mail_info(num)
            except Exception as e:
                logger.info(f"im error：{str(e)}")
                continue
            # 判断其id是否符合查询要求
            if (
                (not (sender_text or receiver_text or theme_text or content_text))
                or sender_text
                and mail_info["from"]
                and sender_text in " ".join([item for item in mail_info["from"] if item])
                or receiver_text
                and mail_info["to"]
                and receiver_text in " ".join([item for item in mail_info["to"] if item])
                or theme_text
                and mail_info["subject"]
                and theme_text in mail_info["subject"]
                or content_text
                and mail_info["body"]
                and content_text in mail_info["body"]
            ):
                logger.info(f"im append：{str(num)}")
                mail_ids.append(num)
            else:
                logger.info(f"im continue：{str(num)}")
                continue

            # 满足最大返回条件即可结束
            if len(mail_ids) == max_return_num:
                break

        logger.info(f"mail id:{mail_ids}")

        # 获取邮件详细信息，并存储附件
        return_mail_res = []
        for mail_id in mail_ids:
            mail_info = core.get_entire_mail_info(mail_id)
            # 判断是否需要保存附件
            if save_attachment_flag:
                for attachment in mail_info["attachments"]:
                    if not attachment:
                        continue
                    with open(os.path.join(save_attachment_path, attachment["name"]), "wb") as f:
                        f.write(attachment["data"])
            # 判断是否需要标注为已读
            if mask_as_read_flag:
                core.mask_as_read(mail_id)
            mail_info["attachments"] = [
                attachment["name"] for attachment in mail_info["attachments"] if attachment and attachment["name"]
            ]
            return_mail_res.append(mail_info)
        return return_mail_res
