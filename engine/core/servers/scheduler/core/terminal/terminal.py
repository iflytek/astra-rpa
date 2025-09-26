import json
import os.path
import platform
import socket
import sys

import psutil
import requests

from ...logger import logger


class Terminal:
    @staticmethod
    def register(svc):
        api = "/api/robot/terminal/register"
        try:
            if not terminal_id:
                logger.error("terminal_id 为空")
                return
            data = {
                "terminalId": terminal_id,  # 终端唯一标识，如设备mac地址
                "name": Terminal.get_device_name(),  # 终端名称
                "account": Terminal.get_account(),  # 设备账号
                "os": Terminal.get_os_info(),  # 操作系统
                "port": svc.route_port,
                "ip": ",".join(ips),  # IP地址
                "status": (
                    "busy" if svc.executor_mg.status() else "free"
                ),  # 当前状态，用于计算最终状态，只有两种状态，运行中busy，空闲free
                "cpu": int(Terminal.get_cpu_percent()),  # CPU占用率（百分比)
                "memory": int(Terminal.get_memory_percent()),  # 内存占用率（百分比)
                "disk": int(Terminal.get_disk_percent()),  # 硬盘占用率（百分比)
                "isDispatch": (1 if svc.terminal_mod else 0),  # 是否调度模式 (0: 否, 1: 是)
                "monitorUrl": "/terminal/ping",  # 视频监控URL
            }
            logger.info("Terminal register data: {}".format(data))
            response = requests.post(
                url="http://127.0.0.1:{}{}".format(svc.route_port, api),
                json=data,
                timeout=10,
            )
            status_code = response.status_code
            text = response.text
            if status_code != 200:
                raise Exception("get error status_code: {}".format(status_code))
            return json.loads(text.strip())["data"]
        except Exception as e:
            logger.exception("[APP] request api: {} error: {}".format(api, e))

    @staticmethod
    def upload(svc):
        api = "/api/robot/terminal/beat"
        try:
            if not terminal_id:
                logger.error("terminal_id 为空")
                return
            data = {
                "terminalId": terminal_id,  # 终端唯一标识，如设备mac地址
                "status": (
                    "busy" if svc.executor_mg.status() else "free"
                ),  # 当前状态，用于计算最终状态，只有两种状态，运行中busy，空闲free
                "isDispatch": (1 if svc.terminal_mod else 0),  # 是否调度模式 (0: 否, 1: 是)
                "cpu": int(Terminal.get_cpu_percent()),  # CPU占用率（百分比)
                "memory": int(Terminal.get_memory_percent()),  # 内存占用率（百分比)
                "disk": int(Terminal.get_disk_percent()),  # 硬盘占用率（百分比)
            }
            logger.info("Terminal upload data: {}".format(data))
            response = requests.post(
                url="http://127.0.0.1:{}{}".format(svc.route_port, api),
                json=data,
                timeout=10,
            )
            status_code = response.status_code
            text = response.text
            if status_code != 200:
                raise Exception("get error status_code: {}".format(status_code))
            res = json.loads(text.strip())
            if "data" not in res:
                # 没有登录，返回None
                return None
            return json.loads(text.strip())["data"]
        except Exception as e:
            logger.exception("[APP] request api: {} error: {}".format(api, e))

    @staticmethod
    def get_terminal_id():
        if len(ip_address) > 0:
            return ip_address[0].get("mac", "")
        return ""

    @staticmethod
    def get_ip_address() -> list:
        """获取本机非回环IPv4地址，优先WLAN，其次有线，再取第一个"""

        def net_priority(net):
            # 排序规则
            iface = net["interface"].lower()
            if any(k in iface for k in ["wlan", "wi-fi", "wifi"]):
                return 0
            if any(k in iface for k in ["eth", "en", "以太网"]):
                return 1
            return 2

        try:
            active_net = []
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            for iface, addresses in addrs.items():
                if not stats[iface].isup:
                    # 跳过未启用的接口
                    continue

                # Linux下过滤更多虚拟接口
                if iface.startswith(
                    (
                        "lo",
                        "virbr",
                        "docker",
                        "veth",
                        "br-",
                        "vmnet",
                        "vboxnet",
                        "tun",
                        "tap",
                    )
                ):
                    # 跳过本地回环和虚拟接口, 如Docker、VMware、VirtualBox等
                    continue

                mac = None
                ipv4 = None
                for addr in addresses:
                    if addr.family == psutil.AF_LINK:
                        mac = addr.address.replace("-", ":").upper()
                for addr in addresses:
                    if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                        ipv4 = addr.address
                if mac and ipv4:
                    active_net.append({"interface": iface, "mac": mac, "ipv4": ipv4})
            return sorted(active_net, key=net_priority)
        except Exception as e:
            logger.error("获取IP地址失败: {}".format(e))
            return []

    @staticmethod
    def get_disk_percent() -> float:
        """
        获取安装目录的盘符, 并计算利用率
        """
        try:
            abs_path = os.path.abspath(__file__)
            if sys.platform == "win32":
                drive = os.path.splitdrive(abs_path)[0]
                logger.info("disk percent: {}".format(drive))
                return psutil.disk_usage(drive).percent
            else:
                root_path = "/"
                return psutil.disk_usage(root_path).percent
        except Exception as e:
            logger.error("获取磁盘使用率失败: {}".format(e))
            return 0.0

    @staticmethod
    def get_cpu_percent() -> float:
        """
        获取CPU利用率
        """
        try:
            ls = psutil.cpu_percent(interval=1, percpu=True)
            return sum(ls) / len(ls)
        except Exception as e:
            logger.error("获取CPU使用率失败: {}".format(e))
            return 0.0

    @staticmethod
    def get_memory_percent() -> float:
        """
        获取内存利用率
        """
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            logger.error("获取内存使用率失败: {}".format(e))
            return 0.0

    @staticmethod
    def get_device_name() -> str:
        """获取设备全名（不包括域，类似hostname）"""
        try:
            return socket.gethostname()
        except Exception as e:
            logger.error("获取设备名称失败: {}".format(e))
            return ""

    @staticmethod
    def get_account() -> str:
        """获取当前登录账号（兼容Windows/Linux/macOS）"""
        try:
            # 优先尝试os.getlogin()
            return os.getlogin()
        except Exception as e:
            logger.error("获取用户账号失败: {}".format(e))
            return ""

    @staticmethod
    def get_os_info() -> str:
        """获取操作系统信息"""
        try:
            system = platform.system()
            if system == "Windows":
                version = platform.version()
                if version >= "10.0.22000":
                    return "Windows 11"
                else:
                    return f"Windows {platform.release()}"
            else:
                return f"{system} {platform.release()}"
        except Exception as e:
            logger.error("获取操作系统信息失败: {}".format(e))
            return ""


ip_address = Terminal.get_ip_address()
ips = [v.get("ipv4") for v in ip_address]
terminal_id = Terminal.get_terminal_id()
