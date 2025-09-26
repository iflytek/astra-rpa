import ast
import json
from typing import Any

from rpaatomic import DynamicsItem
from rpaatomic.atomic import atomicMg

from rpadataprocess import VariableType
from rpadataprocess.error import *


class DataProcess:
    @staticmethod
    @atomicMg.atomic(
        "DataProcess",
        inputList=[atomicMg.param("value", types="Any")],
        outputList=[
            atomicMg.param(
                "variable_var",
                types="Str",
                dynamics=[
                    DynamicsItem(
                        key="$this.variable_var.types",
                        expression="return ['int','str', 'float', 'bool', 'list', 'dict'].includes($this.variable_type.value) ? $this.variable_type.value[0].toUpperCase() + $this.variable_type.value.slice(1) : 'Any'",
                    )
                ],
            ),
        ],
    )
    def set_variable_value(value: Any, variable_type: VariableType = VariableType.INT):
        if variable_type != variable_type.OTHER:
            value = str(value)

        try:
            if variable_type == VariableType.INT:
                result = int(float(value))
            elif variable_type == VariableType.FLOAT:
                result = float(value)
            elif variable_type == VariableType.STR:
                result = str(value)
            elif variable_type == VariableType.BOOL:
                if value in ["True", "true", "1", True, 1]:
                    result = True
                elif value in ["False", "false", "0", False, 0]:
                    result = False
                else:
                    result = bool(value)
            elif variable_type in [
                VariableType.LIST,
                VariableType.DICT,
                VariableType.TUPLE,
            ]:
                result = ast.literal_eval(value)
            elif variable_type == VariableType.JSON:
                result = json.loads(value)
            else:
                result = value
        except Exception as e:
            raise BaseException(VALUE_ERROR_FORMAT.format(e), "输入数据类型有误，无法设置为变量")
        return result
