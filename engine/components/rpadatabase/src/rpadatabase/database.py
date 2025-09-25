import ast
import platform
import sys

from rpaatomic.atomic import atomicMg
from rpadatabase import DatabaseType
from rpadatabase.core import IDatabaseCore
from rpadatabase.error import *

if sys.platform == "win32":
    from rpadatabase.core_win import DatabaseCore
elif platform.system() == "Linux":
    from rpadatabase.core_unix import DatabaseCore
else:
    raise NotImplementedError("Your platform (%s) is not supported by (%s)." % (platform.system(), "clipboard"))


DatabaseCore: IDatabaseCore = DatabaseCore()


class Database:
    @staticmethod
    @atomicMg.atomic(
        "Database",
        intputList=[
            atomicMg.param("connect_info", types=dict),  # TODO 確定類型【目前用手動輸入Dict的方式】
        ],
        outputList=[atomicMg.param("connect_db_obj", types="Any")],
    )
    def connect_database(connect_info: dict, db_type: DatabaseType = DatabaseType.MySQL):
        connect_db_obj = DatabaseCore.connect(connect_info, db_type)
        return connect_db_obj

    @staticmethod
    @atomicMg.atomic("Database", intputList=[], outputList=[])
    def disconnect_database(database_obj: object):
        DatabaseCore.disconnect(database_obj)
        return

    @staticmethod
    @atomicMg.atomic("Database", intputList=[], outputList=[])
    def execute_sql(database_obj: object, sql: str):
        DatabaseCore.execute(database_obj, sql)

    @staticmethod
    @atomicMg.atomic(
        "Database",
        intputList=[],
        outputList=[atomicMg.param("query_db_result", types="Any")],
    )
    def query_sql(database_obj: object, sql: str):
        query_db_result = DatabaseCore.execute(database_obj, sql)
        return query_db_result
