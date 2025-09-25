import os

from rpaframe import logger

from ..utils.win import Registry


def run_reg_file(plugin_id):
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        policy_reg_path = os.path.join(project_root, "policy", "policy.reg")

        if not Registry.exist(r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist"):
            os.startfile(policy_reg_path)
            logger.info("已执行注册表文件")
            return True
        else:
            values = Registry.query_value(r"Software\Policies\Google\Chrome\ExtensionInstallAllowlist")
            logger.info(f"ExtensionInstallAllowlist values {values}")
            if plugin_id in values:
                logger.info("注册表文件已存在且包含指定 plugin_id")
                return True
            else:
                os.startfile(policy_reg_path)
                logger.info("覆盖执行注册表文件")
            return False
    except Exception as e:
        logger.error(f"执行注册表文件失败: {e}")
        return False
