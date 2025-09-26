"""策略核心模块 - 兼容性导入"""

# 为了保持向后兼容性，重新导出类型和管理器
from .manager import Strategy
from .types import StrategyEnv, StrategySvc

# 导出所有类型供其他模块使用
__all__ = ["Strategy", "StrategyEnv", "StrategySvc"]
