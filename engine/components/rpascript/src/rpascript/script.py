import builtins
from inspect import isfunction

from rpaatomic import AtomicFormType, AtomicFormTypeMeta
from rpaatomic.atomic import atomicMg
from rpaatomic.report import report


class Script:
    @staticmethod
    @atomicMg.atomic(
        "Script",
        inputList=[
            atomicMg.param(
                "content",
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.SELECT.value,
                    params={
                        "filters": "PyModule",
                    },
                ),
            )
        ],
        outputList=[atomicMg.param("program_script", types="Any")],
    )
    def module(content: str = "", **kwargs):
        env = kwargs.get("__env__", {})
        project_id = kwargs.get("__project_id__")
        env_dict = env.to_dict(project_id)

        builtins.GLOBAL_RPA_REPORT = report

        temp_dict = {}
        exec(content, temp_dict, None)
        temp_dict["logger"] = report
        main_func = temp_dict.get("main")
        if main_func and isfunction(main_func):
            ret = main_func(**env_dict)
            return ret
