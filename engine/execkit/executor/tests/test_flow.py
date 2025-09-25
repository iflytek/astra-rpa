import json
from unittest import TestCase

from rpa_executor.executor import flow_to_token
from rpa_executor.flow.syntax.lexer import Lexer
from rpa_executor.flow.syntax.parser import Parser


class TestFlow(TestCase):
    def test_flow_if_1(self):
        json_str = """
        [
    {
        "key": "Code.If",
        "title": "IF条件",
        "version": "1",
        "comment": "如果(@{args1})(@{condition})(@{args2})，则执行以下操作",
        "inputList": [
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "args1",
                "title": "对象1",
                "name": "args1",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "1"
                    }
                ]
            },
            {
                "types": "Str",
                "formType": {
                    "type": "SELECT"
                },
                "key": "condition",
                "title": "关系",
                "name": "condition",
                "options": [
                    {
                        "label": "等于",
                        "value": "=="
                    },
                    {
                        "label": "不等于",
                        "value": "!="
                    },
                    {
                        "label": "大于",
                        "value": ">"
                    },
                    {
                        "label": "大于等于",
                        "value": ">="
                    },
                    {
                        "label": "小于",
                        "value": "<"
                    },
                    {
                        "label": "小于等于",
                        "value": "<="
                    }
                ],
                "default": "==",
                "value": "=="
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "args2",
                "title": "对象2",
                "name": "args2",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "1"
                    }
                ]
            }
        ],
        "icon": "icon-list-conditions-if",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "IF条件",
        "id": "bh644194644320325",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "IF条件"
                    }
                ],
                "groupId": "bh644194644336709"
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "IF条件"
                    }
                ],
                "groupId": "bh644194644336709"
            }
        ],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": true,
        "relationEndId": "bh644194644336709",
        "currentIdx": 0,
        "parentIds": [],
        "childrenIds": [
            "bh644194702790725",
            "bh644194702794821",
            "bh644195594149957",
            "bh644195594149958",
            "bh644195653156933",
            "bh644195653156934"
        ],
        "isHide": false,
        "rowNum": 1
    },
    {
        "key": "Code.If",
        "title": "IF条件",
        "version": "1",
        "comment": "如果(@{args1})(@{condition})(@{args2})，则执行以下操作",
        "inputList": [
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "args1",
                "title": "对象1",
                "name": "args1",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "1"
                    }
                ]
            },
            {
                "types": "Str",
                "formType": {
                    "type": "SELECT"
                },
                "key": "condition",
                "title": "关系",
                "name": "condition",
                "options": [
                    {
                        "label": "等于",
                        "value": "=="
                    },
                    {
                        "label": "不等于",
                        "value": "!="
                    },
                    {
                        "label": "大于",
                        "value": ">"
                    },
                    {
                        "label": "大于等于",
                        "value": ">="
                    },
                    {
                        "label": "小于",
                        "value": "<"
                    },
                    {
                        "label": "小于等于",
                        "value": "<="
                    }
                ],
                "default": "==",
                "value": "=="
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "args2",
                "title": "对象2",
                "name": "args2",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "1"
                    }
                ]
            }
        ],
        "icon": "icon-list-conditions-if",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "IF条件",
        "id": "bh644194702790725",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "IF条件"
                    }
                ],
                "groupId": "bh644194702794821"
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "IF条件"
                    }
                ],
                "groupId": "bh644194702794821"
            }
        ],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": true,
        "relationEndId": "bh644194702794821",
        "currentIdx": 1,
        "parentIds": [
            "bh644194644320325"
        ],
        "childrenIds": [
            "bh644194729467973"
        ],
        "isHide": false,
        "rowNum": 2
    },
    {
        "key": "Report.print",
        "title": "日志打印",
        "version": "1",
        "src": "rpareport.report.Report().print",
        "comment": "将变量(@{msg})打印",
        "inputList": [
            {
                "types": "ReportLevelType",
                "formType": {
                    "type": "SELECT"
                },
                "key": "report_type",
                "title": "日志类型",
                "name": "report_type",
                "options": [
                    {
                        "label": "调试",
                        "value": "debug"
                    },
                    {
                        "label": "信息",
                        "value": "info"
                    },
                    {
                        "label": "警告",
                        "value": "warning"
                    },
                    {
                        "label": "错误",
                        "value": "error"
                    }
                ],
                "default": "info",
                "required": true,
                "value": "info"
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "msg",
                "title": "日志内容",
                "name": "msg",
                "tip": "打印运行过程中输出的流变量",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "2"
                    }
                ],
                "required": true,
                "share": true
            }
        ],
        "outputList": [],
        "icon": "icon-log-print",
        "helpManual": "",
        "anotherName": "日志打印",
        "id": "bh644194729467973",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            }
        ],
        "advanced": [
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "parentIds": [
            "bh644194644320325",
            "bh644194702790725"
        ],
        "childrenIds": [],
        "isHide": false,
        "rowNum": 3
    },
    {
        "key": "Code.ElseIf",
        "title": "ELSE IF条件",
        "version": "1",
        "comment": "如果(@{args1})(@{condition})(@{args2})，则执行以下操作",
        "inputList": [
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "args1",
                "title": "对象1",
                "name": "args1",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "1"
                    }
                ]
            },
            {
                "types": "Str",
                "formType": {
                    "type": "SELECT"
                },
                "key": "condition",
                "title": "关系",
                "name": "condition",
                "options": [
                    {
                        "label": "等于",
                        "value": "=="
                    },
                    {
                        "label": "不等于",
                        "value": "!="
                    },
                    {
                        "label": "大于",
                        "value": ">"
                    },
                    {
                        "label": "大于等于",
                        "value": ">="
                    },
                    {
                        "label": "小于",
                        "value": "<"
                    },
                    {
                        "label": "小于等于",
                        "value": "<="
                    }
                ],
                "default": "==",
                "value": "=="
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "args2",
                "title": "对象2",
                "name": "args2",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "1"
                    }
                ]
            }
        ],
        "icon": "icon-list-elseif",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "ELSE IF条件",
        "id": "bh644195594149957",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "ELSE IF条件"
                    }
                ],
                "groupId": "bh644195594149958"
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "ELSE IF条件"
                    }
                ],
                "groupId": "bh644195594149958"
            }
        ],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": true,
        "relationEndId": "bh644195594149958",
        "currentIdx": 4,
        "parentIds": [
            "bh644194644320325"
        ],
        "childrenIds": [
            "bh644195606937669"
        ],
        "isHide": false,
        "rowNum": 4
    },
    {
        "key": "Report.print",
        "title": "日志打印",
        "version": "1",
        "src": "rpareport.report.Report().print",
        "comment": "将变量(@{msg})打印",
        "inputList": [
            {
                "types": "ReportLevelType",
                "formType": {
                    "type": "SELECT"
                },
                "key": "report_type",
                "title": "日志类型",
                "name": "report_type",
                "options": [
                    {
                        "label": "调试",
                        "value": "debug"
                    },
                    {
                        "label": "信息",
                        "value": "info"
                    },
                    {
                        "label": "警告",
                        "value": "warning"
                    },
                    {
                        "label": "错误",
                        "value": "error"
                    }
                ],
                "default": "info",
                "required": true,
                "value": "info"
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "msg",
                "title": "日志内容",
                "name": "msg",
                "tip": "打印运行过程中输出的流变量",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "3"
                    }
                ],
                "required": true,
                "share": true
            }
        ],
        "outputList": [],
        "icon": "icon-log-print",
        "helpManual": "",
        "anotherName": "日志打印",
        "id": "bh644195606937669",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            }
        ],
        "advanced": [
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "parentIds": [
            "bh644194644320325",
            "bh644195594149957"
        ],
        "childrenIds": [],
        "isHide": false,
        "rowNum": 5
    },
    {
        "key": "Code.IfEnd",
        "title": "判断结束",
        "version": "1",
        "comment": "判断结束",
        "icon": "icon-list-conditions-if",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "判断结束",
        "id": "bh644194644336709",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "判断结束"
                    }
                ],
                "groupId": "bh644194644320325"
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "判断结束"
                    }
                ],
                "groupId": "bh644194644320325"
            }
        ],
        "inputList": [],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "relationStartId": "bh644194644320325",
        "parentIds": [],
        "childrenIds": [],
        "isHide": false,
        "rowNum": 9
    },
    {
        "key": "Code.Else",
        "title": "Else条件",
        "version": "1",
        "comment": "Else条件",
        "icon": "icon-list-else",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "Else条件",
        "id": "bh644195653156933",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "Else条件"
                    }
                ],
                "groupId": "bh644195653156934"
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "Else条件"
                    }
                ],
                "groupId": "bh644195653156934"
            }
        ],
        "inputList": [],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": true,
        "relationEndId": "bh644195653156934",
        "currentIdx": 7,
        "parentIds": [
            "bh644194644320325"
        ],
        "childrenIds": [
            "bh644195661303877"
        ],
        "isHide": false,
        "rowNum": 6
    },
    {
        "key": "Report.print",
        "title": "日志打印",
        "version": "1",
        "src": "rpareport.report.Report().print",
        "comment": "将变量(@{msg})打印",
        "inputList": [
            {
                "types": "ReportLevelType",
                "formType": {
                    "type": "SELECT"
                },
                "key": "report_type",
                "title": "日志类型",
                "name": "report_type",
                "options": [
                    {
                        "label": "调试",
                        "value": "debug"
                    },
                    {
                        "label": "信息",
                        "value": "info"
                    },
                    {
                        "label": "警告",
                        "value": "warning"
                    },
                    {
                        "label": "错误",
                        "value": "error"
                    }
                ],
                "default": "info",
                "required": true,
                "value": "info"
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "msg",
                "title": "日志内容",
                "name": "msg",
                "tip": "打印运行过程中输出的流变量",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "4"
                    }
                ],
                "required": true,
                "share": true
            }
        ],
        "outputList": [],
        "icon": "icon-log-print",
        "helpManual": "",
        "anotherName": "日志打印",
        "id": "bh644195661303877",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            }
        ],
        "advanced": [
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "parentIds": [
            "bh644194644320325",
            "bh644195653156933"
        ],
        "childrenIds": [],
        "isHide": false,
        "rowNum": 7
    },
    {
        "key": "Code.IfEnd",
        "title": "判断结束",
        "version": "1",
        "comment": "判断结束",
        "icon": "icon-list-conditions-if",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "判断结束",
        "id": "bh644194644336709",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "判断结束"
                    }
                ],
                "groupId": "bh644194644320325"
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "判断结束"
                    }
                ],
                "groupId": "bh644194644320325"
            }
        ],
        "inputList": [],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "relationStartId": "bh644194644320325",
        "parentIds": [],
        "childrenIds": [],
        "isHide": false,
        "rowNum": 9
    }
]
"""
        flow_list = json.loads(json_str)
        lexer = Lexer(flow_list, flow_to_token, None)
        parser = Parser(lexer=lexer)
        program = parser.parse_program()
        print(program)

    def test_flow_try_2(self):
        json_str = """
        [
    {
        "key": "Code.Try",
        "title": "捕获异常（Try)",
        "version": "1",
        "comment": "可能发生异常的try流程，发生异常后执行catch流程，最终执行finally流程",
        "icon": "icon-list-try",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "捕获异常（Try)",
        "id": "bh644199518302277",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "捕获异常（Try)"
                    }
                ],
                "groupId": "bh644199518302278"
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "捕获异常（Try)"
                    }
                ],
                "groupId": "bh644199518302278"
            }
        ],
        "inputList": [],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": true,
        "relationEndId": "bh644199518302278",
        "currentIdx": 0,
        "parentIds": [],
        "childrenIds": [
            "bh644199551377477"
        ],
        "isHide": false,
        "rowNum": 1
    },
    {
        "key": "Report.print",
        "title": "日志打印",
        "version": "1",
        "src": "rpareport.report.Report().print",
        "comment": "将变量(@{msg})打印",
        "inputList": [
            {
                "types": "ReportLevelType",
                "formType": {
                    "type": "SELECT"
                },
                "key": "report_type",
                "title": "日志类型",
                "name": "report_type",
                "options": [
                    {
                        "label": "调试",
                        "value": "debug"
                    },
                    {
                        "label": "信息",
                        "value": "info"
                    },
                    {
                        "label": "警告",
                        "value": "warning"
                    },
                    {
                        "label": "错误",
                        "value": "error"
                    }
                ],
                "default": "info",
                "required": true,
                "value": "info"
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "msg",
                "title": "日志内容",
                "name": "msg",
                "tip": "打印运行过程中输出的流变量",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "1"
                    }
                ],
                "required": true,
                "share": true
            }
        ],
        "outputList": [],
        "icon": "icon-log-print",
        "helpManual": "",
        "anotherName": "日志打印",
        "id": "bh644199551377477",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            }
        ],
        "advanced": [
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "parentIds": [
            "bh644199518302277"
        ],
        "childrenIds": [],
        "isHide": false,
        "rowNum": 2
    },
    {
        "key": "Code.Catch",
        "title": "捕获异常（Catch)",
        "version": "1",
        "icon": "icon-list-catch",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "捕获异常（Catch)",
        "id": "bh644199518302279",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "捕获异常（Catch)"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "捕获异常（Catch)"
                    }
                ]
            }
        ],
        "inputList": [],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": true,
        "relationEndId": "bh644199518302280",
        "currentIdx": 3,
        "parentIds": [],
        "childrenIds": [
            "bh644199559680069"
        ],
        "isHide": false,
        "rowNum": 3
    },
    {
        "key": "Report.print",
        "title": "日志打印",
        "version": "1",
        "src": "rpareport.report.Report().print",
        "comment": "将变量(@{msg})打印",
        "inputList": [
            {
                "types": "ReportLevelType",
                "formType": {
                    "type": "SELECT"
                },
                "key": "report_type",
                "title": "日志类型",
                "name": "report_type",
                "options": [
                    {
                        "label": "调试",
                        "value": "debug"
                    },
                    {
                        "label": "信息",
                        "value": "info"
                    },
                    {
                        "label": "警告",
                        "value": "warning"
                    },
                    {
                        "label": "错误",
                        "value": "error"
                    }
                ],
                "default": "info",
                "required": true,
                "value": "info"
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "msg",
                "title": "日志内容",
                "name": "msg",
                "tip": "打印运行过程中输出的流变量",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "2"
                    }
                ],
                "required": true,
                "share": true
            }
        ],
        "outputList": [],
        "icon": "icon-log-print",
        "helpManual": "",
        "anotherName": "日志打印",
        "id": "bh644199559680069",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            }
        ],
        "advanced": [
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "parentIds": [
            "bh644199518302279"
        ],
        "childrenIds": [],
        "isHide": false,
        "rowNum": 4
    },
    {
        "key": "Code.Finally",
        "title": "捕获异常（Finally)",
        "version": "1",
        "icon": "icon-list-finally",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "捕获异常（Finally)",
        "id": "bh644199534612549",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "捕获异常（Finally)"
                    }
                ],
                "groupId": "bh644199534612550"
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "捕获异常（Finally)"
                    }
                ],
                "groupId": "bh644199534612550"
            }
        ],
        "inputList": [],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": true,
        "relationEndId": "bh644199534612550",
        "currentIdx": 6,
        "parentIds": [],
        "childrenIds": [
            "bh644199566991429"
        ],
        "isHide": false,
        "rowNum": 5
    },
    {
        "key": "Report.print",
        "title": "日志打印",
        "version": "1",
        "src": "rpareport.report.Report().print",
        "comment": "将变量(@{msg})打印",
        "inputList": [
            {
                "types": "ReportLevelType",
                "formType": {
                    "type": "SELECT"
                },
                "key": "report_type",
                "title": "日志类型",
                "name": "report_type",
                "options": [
                    {
                        "label": "调试",
                        "value": "debug"
                    },
                    {
                        "label": "信息",
                        "value": "info"
                    },
                    {
                        "label": "警告",
                        "value": "warning"
                    },
                    {
                        "label": "错误",
                        "value": "error"
                    }
                ],
                "default": "info",
                "required": true,
                "value": "info"
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "msg",
                "title": "日志内容",
                "name": "msg",
                "tip": "打印运行过程中输出的流变量",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "3"
                    }
                ],
                "required": true,
                "share": true
            }
        ],
        "outputList": [],
        "icon": "icon-log-print",
        "helpManual": "",
        "anotherName": "日志打印",
        "id": "bh644199566991429",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            }
        ],
        "advanced": [
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "parentIds": [
            "bh644199534612549"
        ],
        "childrenIds": [],
        "isHide": false,
        "rowNum": 6
    },
    {
        "key": "Code.TryEnd",
        "title": "捕获结束",
        "version": "1",
        "comment": "捕获结束",
        "icon": "icon-list-try",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "捕获结束",
        "id": "bh644199650373702",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "捕获结束"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "捕获结束"
                    }
                ]
            }
        ],
        "inputList": [],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "relationStartId": "bh644199650373701",
        "parentIds": [],
        "childrenIds": [],
        "isHide": true,
        "rowNum": ""
    },
    {
        "key": "Report.print",
        "title": "日志打印",
        "version": "1",
        "src": "rpareport.report.Report().print",
        "comment": "将变量(@{msg})打印",
        "inputList": [
            {
                "types": "ReportLevelType",
                "formType": {
                    "type": "SELECT"
                },
                "key": "report_type",
                "title": "日志类型",
                "name": "report_type",
                "options": [
                    {
                        "label": "调试",
                        "value": "debug"
                    },
                    {
                        "label": "信息",
                        "value": "info"
                    },
                    {
                        "label": "警告",
                        "value": "warning"
                    },
                    {
                        "label": "错误",
                        "value": "error"
                    }
                ],
                "default": "info",
                "required": true,
                "value": "info"
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "msg",
                "title": "日志内容",
                "name": "msg",
                "tip": "打印运行过程中输出的流变量",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "4"
                    }
                ],
                "required": true,
                "share": true
            }
        ],
        "outputList": [],
        "icon": "icon-log-print",
        "helpManual": "",
        "anotherName": "日志打印",
        "id": "bh644199577268293",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            }
        ],
        "advanced": [
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "parentIds": [],
        "childrenIds": [],
        "isHide": false,
        "rowNum": 8
    },
    {
        "key": "Code.Try",
        "title": "捕获异常（Try)",
        "version": "1",
        "comment": "可能发生异常的try流程，发生异常后执行catch流程，最终执行finally流程",
        "icon": "icon-list-try",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "捕获异常（Try)",
        "id": "bh644199650373701",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "捕获异常（Try)"
                    }
                ],
                "groupId": "bh644199650373702"
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "捕获异常（Try)"
                    }
                ],
                "groupId": "bh644199650373702"
            }
        ],
        "inputList": [],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": true,
        "relationEndId": "bh644199650373702",
        "currentIdx": 10,
        "parentIds": [],
        "childrenIds": [
            "bh644199672414277"
        ],
        "isHide": false,
        "rowNum": 9
    },
    {
        "key": "Report.print",
        "title": "日志打印",
        "version": "1",
        "src": "rpareport.report.Report().print",
        "comment": "将变量(@{msg})打印",
        "inputList": [
            {
                "types": "ReportLevelType",
                "formType": {
                    "type": "SELECT"
                },
                "key": "report_type",
                "title": "日志类型",
                "name": "report_type",
                "options": [
                    {
                        "label": "调试",
                        "value": "debug"
                    },
                    {
                        "label": "信息",
                        "value": "info"
                    },
                    {
                        "label": "警告",
                        "value": "warning"
                    },
                    {
                        "label": "错误",
                        "value": "error"
                    }
                ],
                "default": "info",
                "required": true,
                "value": "info"
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "msg",
                "title": "日志内容",
                "name": "msg",
                "tip": "打印运行过程中输出的流变量",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "5"
                    }
                ],
                "required": true,
                "share": true
            }
        ],
        "outputList": [],
        "icon": "icon-log-print",
        "helpManual": "",
        "anotherName": "日志打印",
        "id": "bh644199672414277",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            }
        ],
        "advanced": [
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "parentIds": [
            "bh644199650373701"
        ],
        "childrenIds": [],
        "isHide": false,
        "rowNum": 10
    },
    {
        "key": "Code.Catch",
        "title": "捕获异常（Catch)",
        "version": "1",
        "icon": "icon-list-catch",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "捕获异常（Catch)",
        "id": "bh644199650377797",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "捕获异常（Catch)"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "捕获异常（Catch)"
                    }
                ]
            }
        ],
        "inputList": [],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": true,
        "relationEndId": "bh644199650377798",
        "currentIdx": 13,
        "parentIds": [],
        "childrenIds": [
            "bh644199682203717"
        ],
        "isHide": false,
        "rowNum": 11
    },
    {
        "key": "Report.print",
        "title": "日志打印",
        "version": "1",
        "src": "rpareport.report.Report().print",
        "comment": "将变量(@{msg})打印",
        "inputList": [
            {
                "types": "ReportLevelType",
                "formType": {
                    "type": "SELECT"
                },
                "key": "report_type",
                "title": "日志类型",
                "name": "report_type",
                "options": [
                    {
                        "label": "调试",
                        "value": "debug"
                    },
                    {
                        "label": "信息",
                        "value": "info"
                    },
                    {
                        "label": "警告",
                        "value": "warning"
                    },
                    {
                        "label": "错误",
                        "value": "error"
                    }
                ],
                "default": "info",
                "required": true,
                "value": "info"
            },
            {
                "types": "Any",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "msg",
                "title": "日志内容",
                "name": "msg",
                "tip": "打印运行过程中输出的流变量",
                "default": "",
                "value": [
                    {
                        "type": "other",
                        "value": "6"
                    }
                ],
                "required": true,
                "share": true
            }
        ],
        "outputList": [],
        "icon": "icon-log-print",
        "helpManual": "",
        "anotherName": "日志打印",
        "id": "bh644199682203717",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "日志打印"
                    }
                ]
            }
        ],
        "advanced": [
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "parentIds": [
            "bh644199650377797"
        ],
        "childrenIds": [],
        "isHide": false,
        "rowNum": 12
    },
    {
        "key": "Code.TryEnd",
        "title": "捕获结束",
        "version": "1",
        "comment": "捕获结束",
        "icon": "icon-list-try",
        "noAdvanced": true,
        "helpManual": "",
        "anotherName": "捕获结束",
        "id": "bh644199650373702",
        "baseForm": [
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": []
                    }
                },
                "title": "任务名称",
                "key": "baseName",
                "noInput": true,
                "value": [
                    {
                        "type": "str",
                        "value": "捕获结束"
                    }
                ]
            },
            {
                "formType": {
                    "type": "INPUT",
                    "params": {
                        "values": [
                            "string"
                        ]
                    }
                },
                "title": "任务别名",
                "key": "anotherName",
                "value": [
                    {
                        "type": "str",
                        "value": "捕获结束"
                    }
                ]
            }
        ],
        "inputList": [],
        "outputList": [],
        "advanced": [
            {
                "types": "Bool",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__res_print__",
                "title": "打印输出变量值",
                "name": "__res_print__",
                "options": [
                    {
                        "label": "是",
                        "value": true
                    },
                    {
                        "label": "否",
                        "value": false
                    }
                ],
                "default": false,
                "value": false
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON",
                    "params": {}
                },
                "key": "__delay_before__",
                "title": "执行前延迟(秒)",
                "name": "__delay_before__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            },
            {
                "types": "Float",
                "formType": {
                    "type": "INPUT_VARIABLE_PYTHON"
                },
                "key": "__delay_after__",
                "title": "执行后延迟(秒)",
                "name": "__delay_after__",
                "default": 0,
                "value": [
                    {
                        "type": "other",
                        "value": 0
                    }
                ]
            }
        ],
        "exception": [
            {
                "types": "Str",
                "formType": {
                    "type": "RADIO",
                    "params": {}
                },
                "key": "__skip_err__",
                "title": "执行异常时",
                "name": "__skip_err__",
                "options": [
                    {
                        "label": "退出",
                        "value": "exit"
                    },
                    {
                        "label": "跳过",
                        "value": "skip"
                    }
                ],
                "default": "exit",
                "value": "exit"
            }
        ],
        "isOpen": false,
        "relationStartId": "bh644199650373701",
        "parentIds": [],
        "childrenIds": [],
        "isHide": true,
        "rowNum": ""
    }
]
       """
        flow_list = json.loads(json_str)
        lexer = Lexer(flow_list, flow_to_token, None)
        parser = Parser(lexer=lexer)
        program = parser.parse_program()
        print(program)

    def test_exist_1(self):
        json_str = """
                [
            {
                "key": "CV.is_image_exist",
                "title": "IF条件",
                "version": "1",
                "comment": "如果(@{args1})(@{condition})(@{args2})，则执行以下操作",
                "inputList": [
                    {
                        "types": "Any",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "args1",
                        "title": "对象1",
                        "name": "args1",
                        "default": "",
                        "value": [
                            {
                                "type": "other",
                                "value": "1"
                            }
                        ]
                    },
                    {
                        "types": "Str",
                        "formType": {
                            "type": "SELECT"
                        },
                        "key": "condition",
                        "title": "关系",
                        "name": "condition",
                        "options": [
                            {
                                "label": "等于",
                                "value": "=="
                            },
                            {
                                "label": "不等于",
                                "value": "!="
                            },
                            {
                                "label": "大于",
                                "value": ">"
                            },
                            {
                                "label": "大于等于",
                                "value": ">="
                            },
                            {
                                "label": "小于",
                                "value": "<"
                            },
                            {
                                "label": "小于等于",
                                "value": "<="
                            }
                        ],
                        "default": "==",
                        "value": "=="
                    },
                    {
                        "types": "Any",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "args2",
                        "title": "对象2",
                        "name": "args2",
                        "default": "",
                        "value": [
                            {
                                "type": "other",
                                "value": "1"
                            }
                        ]
                    }
                ],
                "icon": "icon-list-conditions-if",
                "noAdvanced": true,
                "helpManual": "",
                "anotherName": "IF条件",
                "id": "bh644194702790725",
                "baseForm": [
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": []
                            }
                        },
                        "title": "任务名称",
                        "key": "baseName",
                        "noInput": true,
                        "value": [
                            {
                                "type": "str",
                                "value": "IF条件"
                            }
                        ],
                        "groupId": "bh644194702794821"
                    },
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": [
                                    "string"
                                ]
                            }
                        },
                        "title": "任务别名",
                        "key": "anotherName",
                        "value": [
                            {
                                "type": "str",
                                "value": "IF条件"
                            }
                        ],
                        "groupId": "bh644194702794821"
                    }
                ],
                "outputList": [],
                "advanced": [
                    {
                        "types": "Bool",
                        "formType": {
                            "type": "RADIO",
                            "params": {}
                        },
                        "key": "__res_print__",
                        "title": "打印输出变量值",
                        "name": "__res_print__",
                        "options": [
                            {
                                "label": "是",
                                "value": true
                            },
                            {
                                "label": "否",
                                "value": false
                            }
                        ],
                        "default": false,
                        "value": false
                    },
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON",
                            "params": {}
                        },
                        "key": "__delay_before__",
                        "title": "执行前延迟(秒)",
                        "name": "__delay_before__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    },
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "__delay_after__",
                        "title": "执行后延迟(秒)",
                        "name": "__delay_after__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    }
                ],
                "exception": [
                    {
                        "types": "Str",
                        "formType": {
                            "type": "RADIO",
                            "params": {}
                        },
                        "key": "__skip_err__",
                        "title": "执行异常时",
                        "name": "__skip_err__",
                        "options": [
                            {
                                "label": "退出",
                                "value": "exit"
                            },
                            {
                                "label": "跳过",
                                "value": "skip"
                            }
                        ],
                        "default": "exit",
                        "value": "exit"
                    }
                ],
                "isOpen": true,
                "relationEndId": "bh644194702794821",
                "currentIdx": 1,
                "parentIds": [
                    "bh644194644320325"
                ],
                "childrenIds": [
                    "bh644194729467973"
                ],
                "isHide": false,
                "rowNum": 2
            },
            {
                "key": "Report.print",
                "title": "日志打印",
                "version": "1",
                "src": "rpareport.report.Report().print",
                "comment": "将变量(@{msg})打印",
                "inputList": [
                    {
                        "types": "ReportLevelType",
                        "formType": {
                            "type": "SELECT"
                        },
                        "key": "report_type",
                        "title": "日志类型",
                        "name": "report_type",
                        "options": [
                            {
                                "label": "调试",
                                "value": "debug"
                            },
                            {
                                "label": "信息",
                                "value": "info"
                            },
                            {
                                "label": "警告",
                                "value": "warning"
                            },
                            {
                                "label": "错误",
                                "value": "error"
                            }
                        ],
                        "default": "info",
                        "required": true,
                        "value": "info"
                    },
                    {
                        "types": "Any",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "msg",
                        "title": "日志内容",
                        "name": "msg",
                        "tip": "打印运行过程中输出的流变量",
                        "default": "",
                        "value": [
                            {
                                "type": "other",
                                "value": "2"
                            }
                        ],
                        "required": true,
                        "share": true
                    }
                ],
                "outputList": [],
                "icon": "icon-log-print",
                "helpManual": "",
                "anotherName": "日志打印",
                "id": "bh644194729467973",
                "baseForm": [
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": []
                            }
                        },
                        "title": "任务名称",
                        "key": "baseName",
                        "noInput": true,
                        "value": [
                            {
                                "type": "str",
                                "value": "日志打印"
                            }
                        ]
                    },
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": [
                                    "string"
                                ]
                            }
                        },
                        "title": "任务别名",
                        "key": "anotherName",
                        "value": [
                            {
                                "type": "str",
                                "value": "日志打印"
                            }
                        ]
                    }
                ],
                "advanced": [
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON",
                            "params": {}
                        },
                        "key": "__delay_before__",
                        "title": "执行前延迟(秒)",
                        "name": "__delay_before__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    },
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "__delay_after__",
                        "title": "执行后延迟(秒)",
                        "name": "__delay_after__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    }
                ],
                "exception": [
                    {
                        "types": "Str",
                        "formType": {
                            "type": "RADIO",
                            "params": {}
                        },
                        "key": "__skip_err__",
                        "title": "执行异常时",
                        "name": "__skip_err__",
                        "options": [
                            {
                                "label": "退出",
                                "value": "exit"
                            },
                            {
                                "label": "跳过",
                                "value": "skip"
                            }
                        ],
                        "default": "exit",
                        "value": "exit"
                    }
                ],
                "isOpen": false,
                "parentIds": [
                    "bh644194644320325",
                    "bh644194702790725"
                ],
                "childrenIds": [],
                "isHide": false,
                "rowNum": 3
            },
            {
                "key": "Code.ElseIf",
                "title": "ELSE IF条件",
                "version": "1",
                "comment": "如果(@{args1})(@{condition})(@{args2})，则执行以下操作",
                "inputList": [
                    {
                        "types": "Any",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "args1",
                        "title": "对象1",
                        "name": "args1",
                        "default": "",
                        "value": [
                            {
                                "type": "other",
                                "value": "1"
                            }
                        ]
                    },
                    {
                        "types": "Str",
                        "formType": {
                            "type": "SELECT"
                        },
                        "key": "condition",
                        "title": "关系",
                        "name": "condition",
                        "options": [
                            {
                                "label": "等于",
                                "value": "=="
                            },
                            {
                                "label": "不等于",
                                "value": "!="
                            },
                            {
                                "label": "大于",
                                "value": ">"
                            },
                            {
                                "label": "大于等于",
                                "value": ">="
                            },
                            {
                                "label": "小于",
                                "value": "<"
                            },
                            {
                                "label": "小于等于",
                                "value": "<="
                            }
                        ],
                        "default": "==",
                        "value": "=="
                    },
                    {
                        "types": "Any",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "args2",
                        "title": "对象2",
                        "name": "args2",
                        "default": "",
                        "value": [
                            {
                                "type": "other",
                                "value": "1"
                            }
                        ]
                    }
                ],
                "icon": "icon-list-elseif",
                "noAdvanced": true,
                "helpManual": "",
                "anotherName": "ELSE IF条件",
                "id": "bh644195594149957",
                "baseForm": [
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": []
                            }
                        },
                        "title": "任务名称",
                        "key": "baseName",
                        "noInput": true,
                        "value": [
                            {
                                "type": "str",
                                "value": "ELSE IF条件"
                            }
                        ],
                        "groupId": "bh644195594149958"
                    },
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": [
                                    "string"
                                ]
                            }
                        },
                        "title": "任务别名",
                        "key": "anotherName",
                        "value": [
                            {
                                "type": "str",
                                "value": "ELSE IF条件"
                            }
                        ],
                        "groupId": "bh644195594149958"
                    }
                ],
                "outputList": [],
                "advanced": [
                    {
                        "types": "Bool",
                        "formType": {
                            "type": "RADIO",
                            "params": {}
                        },
                        "key": "__res_print__",
                        "title": "打印输出变量值",
                        "name": "__res_print__",
                        "options": [
                            {
                                "label": "是",
                                "value": true
                            },
                            {
                                "label": "否",
                                "value": false
                            }
                        ],
                        "default": false,
                        "value": false
                    },
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON",
                            "params": {}
                        },
                        "key": "__delay_before__",
                        "title": "执行前延迟(秒)",
                        "name": "__delay_before__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    },
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "__delay_after__",
                        "title": "执行后延迟(秒)",
                        "name": "__delay_after__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    }
                ],
                "exception": [
                    {
                        "types": "Str",
                        "formType": {
                            "type": "RADIO",
                            "params": {}
                        },
                        "key": "__skip_err__",
                        "title": "执行异常时",
                        "name": "__skip_err__",
                        "options": [
                            {
                                "label": "退出",
                                "value": "exit"
                            },
                            {
                                "label": "跳过",
                                "value": "skip"
                            }
                        ],
                        "default": "exit",
                        "value": "exit"
                    }
                ],
                "isOpen": true,
                "relationEndId": "bh644195594149958",
                "currentIdx": 4,
                "parentIds": [
                    "bh644194644320325"
                ],
                "childrenIds": [
                    "bh644195606937669"
                ],
                "isHide": false,
                "rowNum": 4
            },
            {
                "key": "Report.print",
                "title": "日志打印",
                "version": "1",
                "src": "rpareport.report.Report().print",
                "comment": "将变量(@{msg})打印",
                "inputList": [
                    {
                        "types": "ReportLevelType",
                        "formType": {
                            "type": "SELECT"
                        },
                        "key": "report_type",
                        "title": "日志类型",
                        "name": "report_type",
                        "options": [
                            {
                                "label": "调试",
                                "value": "debug"
                            },
                            {
                                "label": "信息",
                                "value": "info"
                            },
                            {
                                "label": "警告",
                                "value": "warning"
                            },
                            {
                                "label": "错误",
                                "value": "error"
                            }
                        ],
                        "default": "info",
                        "required": true,
                        "value": "info"
                    },
                    {
                        "types": "Any",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "msg",
                        "title": "日志内容",
                        "name": "msg",
                        "tip": "打印运行过程中输出的流变量",
                        "default": "",
                        "value": [
                            {
                                "type": "other",
                                "value": "3"
                            }
                        ],
                        "required": true,
                        "share": true
                    }
                ],
                "outputList": [],
                "icon": "icon-log-print",
                "helpManual": "",
                "anotherName": "日志打印",
                "id": "bh644195606937669",
                "baseForm": [
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": []
                            }
                        },
                        "title": "任务名称",
                        "key": "baseName",
                        "noInput": true,
                        "value": [
                            {
                                "type": "str",
                                "value": "日志打印"
                            }
                        ]
                    },
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": [
                                    "string"
                                ]
                            }
                        },
                        "title": "任务别名",
                        "key": "anotherName",
                        "value": [
                            {
                                "type": "str",
                                "value": "日志打印"
                            }
                        ]
                    }
                ],
                "advanced": [
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON",
                            "params": {}
                        },
                        "key": "__delay_before__",
                        "title": "执行前延迟(秒)",
                        "name": "__delay_before__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    },
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "__delay_after__",
                        "title": "执行后延迟(秒)",
                        "name": "__delay_after__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    }
                ],
                "exception": [
                    {
                        "types": "Str",
                        "formType": {
                            "type": "RADIO",
                            "params": {}
                        },
                        "key": "__skip_err__",
                        "title": "执行异常时",
                        "name": "__skip_err__",
                        "options": [
                            {
                                "label": "退出",
                                "value": "exit"
                            },
                            {
                                "label": "跳过",
                                "value": "skip"
                            }
                        ],
                        "default": "exit",
                        "value": "exit"
                    }
                ],
                "isOpen": false,
                "parentIds": [
                    "bh644194644320325",
                    "bh644195594149957"
                ],
                "childrenIds": [],
                "isHide": false,
                "rowNum": 5
            },
            {
                "key": "Code.Else",
                "title": "Else条件",
                "version": "1",
                "comment": "Else条件",
                "icon": "icon-list-else",
                "noAdvanced": true,
                "helpManual": "",
                "anotherName": "Else条件",
                "id": "bh644195653156933",
                "baseForm": [
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": []
                            }
                        },
                        "title": "任务名称",
                        "key": "baseName",
                        "noInput": true,
                        "value": [
                            {
                                "type": "str",
                                "value": "Else条件"
                            }
                        ],
                        "groupId": "bh644195653156934"
                    },
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": [
                                    "string"
                                ]
                            }
                        },
                        "title": "任务别名",
                        "key": "anotherName",
                        "value": [
                            {
                                "type": "str",
                                "value": "Else条件"
                            }
                        ],
                        "groupId": "bh644195653156934"
                    }
                ],
                "inputList": [],
                "outputList": [],
                "advanced": [
                    {
                        "types": "Bool",
                        "formType": {
                            "type": "RADIO",
                            "params": {}
                        },
                        "key": "__res_print__",
                        "title": "打印输出变量值",
                        "name": "__res_print__",
                        "options": [
                            {
                                "label": "是",
                                "value": true
                            },
                            {
                                "label": "否",
                                "value": false
                            }
                        ],
                        "default": false,
                        "value": false
                    },
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON",
                            "params": {}
                        },
                        "key": "__delay_before__",
                        "title": "执行前延迟(秒)",
                        "name": "__delay_before__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    },
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "__delay_after__",
                        "title": "执行后延迟(秒)",
                        "name": "__delay_after__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    }
                ],
                "exception": [
                    {
                        "types": "Str",
                        "formType": {
                            "type": "RADIO",
                            "params": {}
                        },
                        "key": "__skip_err__",
                        "title": "执行异常时",
                        "name": "__skip_err__",
                        "options": [
                            {
                                "label": "退出",
                                "value": "exit"
                            },
                            {
                                "label": "跳过",
                                "value": "skip"
                            }
                        ],
                        "default": "exit",
                        "value": "exit"
                    }
                ],
                "isOpen": true,
                "relationEndId": "bh644195653156934",
                "currentIdx": 7,
                "parentIds": [
                    "bh644194644320325"
                ],
                "childrenIds": [
                    "bh644195661303877"
                ],
                "isHide": false,
                "rowNum": 6
            },
            {
                "key": "Report.print",
                "title": "日志打印",
                "version": "1",
                "src": "rpareport.report.Report().print",
                "comment": "将变量(@{msg})打印",
                "inputList": [
                    {
                        "types": "ReportLevelType",
                        "formType": {
                            "type": "SELECT"
                        },
                        "key": "report_type",
                        "title": "日志类型",
                        "name": "report_type",
                        "options": [
                            {
                                "label": "调试",
                                "value": "debug"
                            },
                            {
                                "label": "信息",
                                "value": "info"
                            },
                            {
                                "label": "警告",
                                "value": "warning"
                            },
                            {
                                "label": "错误",
                                "value": "error"
                            }
                        ],
                        "default": "info",
                        "required": true,
                        "value": "info"
                    },
                    {
                        "types": "Any",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "msg",
                        "title": "日志内容",
                        "name": "msg",
                        "tip": "打印运行过程中输出的流变量",
                        "default": "",
                        "value": [
                            {
                                "type": "other",
                                "value": "4"
                            }
                        ],
                        "required": true,
                        "share": true
                    }
                ],
                "outputList": [],
                "icon": "icon-log-print",
                "helpManual": "",
                "anotherName": "日志打印",
                "id": "bh644195661303877",
                "baseForm": [
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": []
                            }
                        },
                        "title": "任务名称",
                        "key": "baseName",
                        "noInput": true,
                        "value": [
                            {
                                "type": "str",
                                "value": "日志打印"
                            }
                        ]
                    },
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": [
                                    "string"
                                ]
                            }
                        },
                        "title": "任务别名",
                        "key": "anotherName",
                        "value": [
                            {
                                "type": "str",
                                "value": "日志打印"
                            }
                        ]
                    }
                ],
                "advanced": [
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON",
                            "params": {}
                        },
                        "key": "__delay_before__",
                        "title": "执行前延迟(秒)",
                        "name": "__delay_before__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    },
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "__delay_after__",
                        "title": "执行后延迟(秒)",
                        "name": "__delay_after__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    }
                ],
                "exception": [
                    {
                        "types": "Str",
                        "formType": {
                            "type": "RADIO",
                            "params": {}
                        },
                        "key": "__skip_err__",
                        "title": "执行异常时",
                        "name": "__skip_err__",
                        "options": [
                            {
                                "label": "退出",
                                "value": "exit"
                            },
                            {
                                "label": "跳过",
                                "value": "skip"
                            }
                        ],
                        "default": "exit",
                        "value": "exit"
                    }
                ],
                "isOpen": false,
                "parentIds": [
                    "bh644194644320325",
                    "bh644195653156933"
                ],
                "childrenIds": [],
                "isHide": false,
                "rowNum": 7
            },
            {
                "key": "Code.IfEnd",
                "title": "判断结束",
                "version": "1",
                "comment": "判断结束",
                "icon": "icon-list-conditions-if",
                "noAdvanced": true,
                "helpManual": "",
                "anotherName": "判断结束",
                "id": "bh644194644336709",
                "baseForm": [
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": []
                            }
                        },
                        "title": "任务名称",
                        "key": "baseName",
                        "noInput": true,
                        "value": [
                            {
                                "type": "str",
                                "value": "判断结束"
                            }
                        ],
                        "groupId": "bh644194644320325"
                    },
                    {
                        "formType": {
                            "type": "INPUT",
                            "params": {
                                "values": [
                                    "string"
                                ]
                            }
                        },
                        "title": "任务别名",
                        "key": "anotherName",
                        "value": [
                            {
                                "type": "str",
                                "value": "判断结束"
                            }
                        ],
                        "groupId": "bh644194644320325"
                    }
                ],
                "inputList": [],
                "outputList": [],
                "advanced": [
                    {
                        "types": "Bool",
                        "formType": {
                            "type": "RADIO",
                            "params": {}
                        },
                        "key": "__res_print__",
                        "title": "打印输出变量值",
                        "name": "__res_print__",
                        "options": [
                            {
                                "label": "是",
                                "value": true
                            },
                            {
                                "label": "否",
                                "value": false
                            }
                        ],
                        "default": false,
                        "value": false
                    },
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON",
                            "params": {}
                        },
                        "key": "__delay_before__",
                        "title": "执行前延迟(秒)",
                        "name": "__delay_before__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    },
                    {
                        "types": "Float",
                        "formType": {
                            "type": "INPUT_VARIABLE_PYTHON"
                        },
                        "key": "__delay_after__",
                        "title": "执行后延迟(秒)",
                        "name": "__delay_after__",
                        "default": 0,
                        "value": [
                            {
                                "type": "other",
                                "value": 0
                            }
                        ]
                    }
                ],
                "exception": [
                    {
                        "types": "Str",
                        "formType": {
                            "type": "RADIO",
                            "params": {}
                        },
                        "key": "__skip_err__",
                        "title": "执行异常时",
                        "name": "__skip_err__",
                        "options": [
                            {
                                "label": "退出",
                                "value": "exit"
                            },
                            {
                                "label": "跳过",
                                "value": "skip"
                            }
                        ],
                        "default": "exit",
                        "value": "exit"
                    }
                ],
                "isOpen": false,
                "relationStartId": "bh644194644320325",
                "parentIds": [],
                "childrenIds": [],
                "isHide": false,
                "rowNum": 9
            }
        ]
        """
        flow_list = json.loads(json_str)
        lexer = Lexer(flow_list, flow_to_token, None)
        parser = Parser(lexer=lexer)
        program = parser.parse_program()
        print(program)
