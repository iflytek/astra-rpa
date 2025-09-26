from typing import Any

from rpaatomic import AtomicFormType, AtomicFormTypeMeta, ReportType, ReportUser
from rpaatomic.atomic import atomicMg
from rpaatomic.report import report

from rpareport import ReportLevelType


class Report:
    @staticmethod
    @atomicMg.atomic(
        "Report",
        inputList=[
            atomicMg.param(
                key="report_type",
                formType=AtomicFormTypeMeta(type=AtomicFormType.SELECT.value),
            ),
        ],
    )
    def print(report_type: ReportLevelType = ReportLevelType.INFO, msg: Any = "", **kwargs) -> None:
        msg = str(msg)

        line = int(kwargs.get("__line__", 0))
        line_id = kwargs.get("__line_id__", "")
        process_name = kwargs.get("__process_name__", "")
        process_id = kwargs.get("__process_id__", "")
        atomic_name = kwargs.get("__atomic_name__", "")

        if report_type == ReportLevelType.INFO:
            report.info(
                ReportUser(
                    log_type=ReportType.User,
                    process=process_name,
                    process_id=process_id,
                    atomic=atomic_name,
                    line=line,
                    line_id=line_id,
                    msg_str=msg,
                )
            )
        elif report_type == ReportLevelType.WARNING:
            report.warning(
                ReportUser(
                    log_type=ReportType.User,
                    process=process_name,
                    process_id=process_id,
                    atomic=atomic_name,
                    line=line,
                    line_id=line_id,
                    msg_str=msg,
                )
            )
        elif report_type == ReportLevelType.ERROR:
            report.error(
                ReportUser(
                    log_type=ReportType.User,
                    process=process_name,
                    process_id=process_id,
                    atomic=atomic_name,
                    line=line,
                    line_id=line_id,
                    msg_str=msg,
                )
            )
        else:
            report.info(
                ReportUser(
                    log_type=ReportType.User,
                    process=process_name,
                    process_id=process_id,
                    atomic=atomic_name,
                    line=line,
                    line_id=line_id,
                    msg_str=msg,
                )
            )
