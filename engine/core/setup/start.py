import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor

from setup.config import config
from setup.logger import logger  # 必须排第一
from setup.server.package_server import Package
from setup.server.process_server import Process


def start(conf_file="conf.json", schema="START"):
    try:
        logger.info("service[:{}] start".format("setup"))

        if schema == "STOP":
            Process.kill_all_zombie()
            return

        # 2. 读取配置，并解析
        conf = conf_file.strip('"')
        conf = conf.replace("\\\\", "\\")
        with open(conf) as f:
            conf_json = json.loads(f.readline().strip())

        config.REMOTE_ADDR = conf_json.get("remote_addr", "")
        config.PYPI_SERVER_REMOTE = conf_json.get("pypi_remote", "")
        if conf_file == "conf.json":
            config.CONF_FILE = os.getcwd() + os.sep + "conf.json"
        else:
            config.CONF_FILE = conf_file

        # 3. 启动
        # Process.kill_all_zombie()  # 清理
        Package.core_package_start()
        with ThreadPoolExecutor() as executor:
            executor.submit(Process.pid_exist_check)
    except Exception as e:
        logger.error("setup error: {}".format(e))


# 保持原有的命令行接口
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="{} service".format("setup"))
    parser.add_argument("--conf", type=str, default="conf.json", help="配置文件")
    parser.add_argument("--schema", type=str, default="START", choices=["START", "STOP"])
    args = parser.parse_args()
    start(args.conf, args.schema)
