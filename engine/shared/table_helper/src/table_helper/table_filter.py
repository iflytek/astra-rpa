import re
from datetime import datetime

import pandas as pd
from rpaframe.logger.logger import logger


def parse_datetime(date_string):
    chinese_to_number = {
        "一": "1",
        "初一": "1",
        "二": "2",
        "初二": "2",
        "三": "3",
        "初三": "3",
        "四": "4",
        "初四": "4",
        "五": "5",
        "初五": "5",
        "六": "6",
        "初六": "6",
        "七": "7",
        "初七": "7",
        "八": "8",
        "初八": "8",
        "九": "9",
        "初九": "9",
        "零": "0",
        "十": "10",
        "初十": "10",
        "十一": "11",
        "十二": "12",
        "十三": "13",
        "十四": "14",
        "十五": "15",
        "十六": "16",
        "十七": "17",
        "十八": "18",
        "十九": "19",
        "二十": "20",
        "二十一": "21",
        "廿一": "21",
        "二十二": "22",
        "廿二": "22",
        "二十三": "23",
        "廿三": "23",
        "二十四": "24",
        "廿四": "24",
        "二十五": "25",
        "廿五": "25",
        "二十六": "26",
        "廿六": "26",
        "二十七": "27",
        "廿七": "27",
        "二十八": "28",
        "廿八": "28",
        "二十九": "29",
        "廿九": "29",
        "三十": "30",
        "三十一": "31",
    }

    # 中文日期格式的正则表达式
    chinese_date_formats = {
        r"^(\d{4})-(\d{1,2})-(\d{1,2})\s(\d{1,2}):(\d{1,2}):(\d{1,2})$": "%Y-%m-%d %H:%M:%S",
        r"^(\d{4})/(\d{1,2})/(\d{1,2})\s(\d{1,2}):(\d{1,2}):(\d{1,2})$": "%Y/%m/%d %H:%M:%S",
        r"^(\d{4})\.(\d{1,2})\.(\d{1,2})\s(\d{1,2}):(\d{1,2}):(\d{1,2})$": "%Y.%m.%d %H:%M:%S",
        r"^(\d{4})年(\d{1,2})月(\d{1,2})日\s(\d{1,2}):(\d{1,2}):(\d{1,2})$": "%Y年%m月%d日 %H:%M:%S",
        r"^(\d{4})-(\d{1,2})-(\d{1,2})T(\d{1,2}):(\d{1,2}):(\d{1,2})$": "%Y-%m-%dT%H:%M:%S",
        r"^(\d{4})年(\d{1,2})月(\d{1,2})日\s(\d{1,2})时(\d{1,2})分(\d{1,2})秒$": "%Y年%m月%d日 %H时%M分%S秒",
        r"^(\d{4})-(\d{1,2})-(\d{1,2})\s(\d{1,2}):(\d{1,2})$": "%Y-%m-%d %H:%M",
        r"^(\d{4})/(\d{1,2})/(\d{1,2})\s(\d{1,2}):(\d{1,2})$": "%Y/%m/%d %H:%M",
        r"^(\d{4})\.(\d{1,2})\.(\d{1,2})\s(\d{1,2}):(\d{1,2})$": "%Y.%m.%d %H:%M",
        r"^(\d{4})年(\d{1,2})月(\d{1,2})日\s(\d{1,2}):(\d{1,2})$": "%Y年%m月%d日 %H:%M",
        r"^(\d{4})年(\d{1,2})月(\d{1,2})日\s(\d{1,2})时(\d{1,2})分$": "%Y年%m月%d日 %H时%M分",
        r"^(\d{1,2})-(\d{1,2})\s(\d{1,2}):(\d{1,2}):(\d{1,2})$": "%m-%d %H:%M:%S",
        r"^(\d{1,2})/(\d{1,2})\s(\d{1,2}):(\d{1,2}):(\d{1,2})$": "%m/%d %H:%M:%S",
        r"^(\d{1,2})\.(\d{1,2})\s(\d{1,2}):(\d{1,2}):(\d{1,2})$": "%m.%d %H:%M:%S",
        r"^(\d{1,2})月(\d{1,2})日\s(\d{1,2}):(\d{1,2}):(\d{1,2})$": "%m月%d日 %H:%M:%S",
        r"^(\d{1,2})月(\d{1,2})日\s(\d{1,2}):(\d{1,2})$": "%m月%d日 %H:%M",
        r"^(\d{1,2})月(\d{1,2})日\s(\d{1,2})时(\d{1,2})分(\d{1,2})秒$": "%m月%d日 %H时%M分%S秒",
        r"^(\d{4})-(\d{1,2})-(\d{1,2})$": "%Y-%m-%d",
        r"^(\d{4})/(\d{1,2})/(\d{1,2})$": "%Y/%m/%d",
        r"^(\d{4})\.(\d{1,2})\.(\d{1,2})$": "%Y.%m.%d",
        r"^(\d{4})年(\d{1,2})月(\d{1,2})日$": "%Y年%m月%d日",
        r"^(\d{4})-(\d{1,2})$": "%Y-%m",
        r"^(\d{4})/(\d{1,2})$": "%Y/%m",
        r"^(\d{4})\.(\d{1,2})$": "%Y.%m",
        r"^(\d{4})年(\d{1,2})月$": "%Y年%m月",
        r"^(\d{1,2})-(\d{1,2})$": "%m-%d",
        r"^(\d{1,2})/(\d{1,2})$": "%m/%d",
        r"^(\d{1,2})\.(\d{1,2})$": "%m.%d",
        r"^(\d{1,2})月(\d{1,2})日$": "%m月%d日",
        r"^(\d{1,2}):(\d{1,2}):(\d{1,2})$": "%H:%M:%S",
        r"^(\d{1,2})时(\d{1,2})分(\d{1,2})秒$": "%H时%M分%S秒",
        r"^(\d{1,2}):(\d{1,2})$": "%H:%M",
        r"^(\d{1,2})时(\d{1,2})分$": "%H时%M分",
    }

    if not date_string:
        return ""
    date_format = None
    for pattern, format_str in chinese_date_formats.items():
        match = re.match(pattern, date_string)
        if match:
            for chinese, number in chinese_to_number.items():
                date_string = date_string.replace(chinese, number)
            date_format = datetime.strptime(date_string, format_str)

    if not date_format:
        date_format = date_string
    return date_format


class DataFilter(object):
    def __init__(self, data_json):
        self.data_json = data_json
        self.produceType = data_json.get("produceType")
        self.data_values = data_json.get("values")
        # print(f"self.data_values: {self.data_values}")
        self.value_types = list(map(lambda x: x.get("value_type"), self.data_values))
        # print(f"self.value_types: {self.value_types}")
        self.data_list = list(map(lambda x: x["value"], self.data_values))
        self.cell_filterConfig_list = list(map(lambda x: x.get("colFilterConfig"), self.data_values))
        self.filterConfig_list = list(map(lambda x: x.get("filterConfig"), self.data_values))
        self.dataProcessConfig_list = list(map(lambda x: x.get("colDataProcessConfig"), self.data_values))
        self.hightLightIndex_list = []
        self.dataProcess_state = 0
        self.data_table = self.get_table()
        self.filter_mian = self.data_filter_main()

    def get_table(self):
        """
        将数据转为 DataFrame
        data_json: 抓取的数据
        return:
        """
        if self.produceType == "similar":
            max_length = max(len(sublist) for sublist in self.data_list)
            for one_list in self.data_list:
                while len(one_list) < max_length:
                    one_list.append({"attrs": {}, "text": ""})
            for i, item_list in enumerate(self.data_list):
                for item in item_list:
                    item["text"] = (
                        re.sub(
                            r"[\n\t]|^\s+|\s+$|\xa0",
                            "",
                            item["attrs"].get(self.value_types[i]),
                        )
                        if item["attrs"].get(self.value_types[i])
                        else ""
                    )
            text_values = list(map(lambda x: [item["text"] for item in x], self.data_list))
        elif self.produceType == "table":
            for i, item_list in enumerate(self.data_list):
                self.data_list[i] = [re.sub(r"[\n\t]|^\s+|\s+$|\xa0", "", item) for item in item_list]
            text_values = self.data_list

        else:
            text_values = []
        data_table = pd.DataFrame(text_values).T
        data_table.reset_index(inplace=True)
        self.hightLightIndex_list = [list(data_table["index"]) for _ in range(len(text_values))]
        # print(self.hightLightIndex_list )

        return data_table

    def cell_filter(self):
        """
        单元格过滤
        针对单列操作，筛选后，不改变其它列
        """
        for index in range(len(self.cell_filterConfig_list)):
            if self.cell_filterConfig_list[index]:
                filter_condition = ""
                filter_index = 0
                for condition_one in self.cell_filterConfig_list[index]:
                    filterAssociation = condition_one.get("filterAssociation")
                    logical = condition_one.get("logical")
                    parameter = condition_one.get("parameter")
                    parameter = re.sub(r"[\n\t]|^\s+|\s+$|\xa0", "", parameter)
                    logic_op_map = {"and": "&", "or": "|"}
                    filter_logic_str = self.filter_logic_calc(index, logical, parameter)
                    filter_one_str = f"({filter_logic_str})"
                    if filter_index > 0:
                        filter_one_str = f" {logic_op_map[filterAssociation]} {filter_one_str}"
                    filter_condition += filter_one_str
                    filter_index += 1
                try:
                    filter_df = self.data_table[eval(filter_condition)]
                    self.hightLightIndex_list[index] = list(filter_df["index"])
                    filter_result = list(filter_df[index])
                    self.data_table[index] = ""
                    self.data_table[index].update(filter_result)
                except Exception as e:
                    logger.error(f"cell_filter: {str(e)}")
                    raise ValueError(f"暂不支持该筛选条件：{str(e)}")

    def table_filter(self):
        """
        整张表过滤
        针对整张表操作，筛选后，保留符合条件的整行数据
        """
        for index in range(len(self.filterConfig_list)):
            if self.filterConfig_list[index]:
                filter_condition = ""
                filter_index = 0
                for condition_one in self.filterConfig_list[index]:
                    filterAssociation = condition_one.get("filterAssociation")
                    logical = condition_one.get("logical")
                    parameter = condition_one.get("parameter")
                    parameter = re.sub(r"[\n\t]|^\s+|\s+$|\xa0", "", parameter)
                    logic_op_map = {"and": "&", "or": "|"}
                    filter_logic_str = self.filter_logic_calc(index, logical, parameter)
                    filter_one_str = f"({filter_logic_str})"
                    if filter_index > 0:
                        filter_one_str = f" {logic_op_map[filterAssociation]} {filter_one_str}"
                    filter_condition += filter_one_str
                    filter_index += 1
                try:
                    self.data_table = self.data_table[eval(filter_condition)]
                except Exception as e:
                    logger.error(f"table_filter: {str(e)}")
                    raise ValueError(f"暂不支持该筛选条件：{str(e)}")
        for index in range(len(self.hightLightIndex_list)):
            self.hightLightIndex_list[index] = [
                self.hightLightIndex_list[index][i] for i in list(self.data_table["index"])
            ]

    def filter_logic_calc(self, index, logical, parameter):
        """
        logic_op: ['==', '!=', '>', '<', '>=', '<=', 'isnull', 'notnull', 'enumerate',
                  'startswith', 'endswith', 'contains', 'not_startswith', 'not_endswith', 'not_contains',
                  'time_befor', 'time_after', 'time_between', 'regular']
        """
        filter_logic_str = None
        filter_col_str = f"self.data_table[{index}]"
        if logical in ["==", "!=", ">", "<", ">=", "<="]:
            if logical in ["==", "!="]:
                if parameter.isdigit():
                    self.data_table[index] = pd.to_numeric(self.data_table[index], errors="coerce")
                    parameter = f"{parameter}"
                else:
                    parameter = f'"{parameter}"'
            else:
                self.data_table[index] = pd.to_numeric(self.data_table[index], errors="coerce")
            filter_logic_str = f"{filter_col_str}{logical}{parameter}"
        elif logical in ["startswith", "endswith", "contains"]:
            if logical == "contains":
                parameter = re.escape(parameter)
            filter_logic_str = f'{filter_col_str}.astype(str).str.{logical}("{parameter}")'
        elif logical in ["not_startswith", "not_endswith", "not_contains"]:
            if logical == "not_contains":
                parameter = re.escape(parameter)
            logical = logical.split("_")[1]
            filter_logic_str = f'~{filter_col_str}.astype(str).str.{logical}("{parameter}")'
        elif logical in ["isnull", "notnull"]:
            # filter_logic_str = f'{filter_col_str}.astype(str).{logical}()'
            if logical == "isnull":
                filter_logic_str = f'{filter_col_str}.astype(str)==""'
            else:
                filter_logic_str = f'{filter_col_str}.astype(str)!=""'
        elif logical in ["time_befor", "time_after", "time_between"]:
            self.data_table[index] = self.data_table[index].astype(str)
            if logical == "time_befor":
                filter_logic_str = f"{filter_col_str}<'{parameter}'"
            elif logical == "time_after":
                filter_logic_str = f"{filter_col_str}>'{parameter}'"
            elif logical == "time_between":
                if isinstance(parameter, str):
                    parameter = eval(parameter)
                if isinstance(parameter, list):
                    filter_logic_str = f"({filter_col_str} >= '{parameter[0]}')&({filter_col_str} <= '{parameter[1]}')"
                else:
                    raise ValueError("条件异常，请输入正确的条件！")
        elif logical == "regular":
            filter_logic_str = f'{filter_col_str}.astype(str).str.contains(r"{parameter}", regex=True)'
        elif logical == "enumerate":
            if isinstance(parameter, str):
                parameter = eval(parameter)
            if isinstance(parameter, list):
                filter_logic_str = f"{filter_col_str}.isin({parameter})"
            else:
                raise ValueError("条件异常，请输入正确的条件！")
        else:
            filter_logic_str = None

        return filter_logic_str

    def ExtractNum(self, index, parameters):
        # 提取数字
        self.data_table[index] = list(
            self.data_table[index].astype(str).apply(lambda x: "".join(re.findall(r"\d+", x)))
        )

    def trim(self, index, parameters):
        # 去除首尾空格
        self.data_table[index] = list(
            self.data_table[index]
            .astype(str)
            .str.replace(r"^\s+|\s+?$", "", regex=True)
            .str.replace(r"[\t\n]+", "", regex=True)
        )

    def replace(self, index, parameters):
        # 字符替换
        for parameter in parameters:
            text = re.escape(parameter.get("text"))
            replaceText = parameter.get("replaceText")
            self.data_table[index] = list(self.data_table[index].astype(str).str.replace(text, replaceText))

    def prefix(self, index, parameters):
        # 添加前缀
        val = parameters[0].get("val")
        self.data_table[index] = list(val + self.data_table[index].astype(str))

    def suffix(self, index, parameters):
        # 添加后缀
        val = parameters[0].get("val")
        self.data_table[index] = list(self.data_table[index].astype(str) + val)

    def formatTime(self, index, parameters):
        # 格式化时间
        val = parameters[0].get("val")
        if val != "":
            self.data_table[index] = self.data_table[index].apply(parse_datetime)
            self.data_table[index] = pd.to_datetime(self.data_table[index].astype(str), errors="coerce")
            self.data_table[index] = self.data_table[index].dt.strftime(val.encode("unicode-escape").decode())
            self.data_table[index] = (
                self.data_table[index].fillna("").apply(lambda x: x.encode().decode("unicode-escape"))
            )

    def regular(self, index, parameters):
        # 正则筛选
        val = parameters[0].get("val")
        # self.data_table[index] = self.data_table[index].astype(str).str.extractall(f'({val})')
        extracted = (
            self.data_table[index]
            .astype(str)
            .str.extractall(f"({val})")
            .groupby(level=0)[0]
            .apply(" ".join)
            .reset_index()
        )
        self.data_table[index] = extracted[0]

    def dataProcess(self):
        """
        数据处理：提取数字，去除首尾空格，字符替换，添加前缀，添加后缀，格式化时间，正则筛选
        """
        # 循环列
        self.dataProcess_state = 1
        process_order = [
            "Trim",
            "FormatTime",
            "Regular",
            "Replace",
            "ExtractNum",
            "Prefix",
            "Suffix",
        ]
        for index in range(len(self.dataProcessConfig_list)):
            for process_type in process_order:
                process_type_result = list(
                    filter(
                        lambda x: x["processType"] == process_type and x["isEnable"],
                        self.dataProcessConfig_list[index],
                    )
                )
                if process_type_result != []:
                    process_type = process_type_result[0]["processType"]
                    parameters = process_type_result[0]["parameters"]
                    if process_type in [
                        "Replace",
                        "Prefix",
                        "Suffix",
                        "FormatTime",
                        "Regular",
                    ]:
                        if not parameters:
                            raise ValueError(f"第{index + 1}列数据处理缺少参数")
                    try:
                        if process_type == "Trim":
                            self.trim(index, parameters)
                        elif process_type == "FormatTime":
                            self.formatTime(index, parameters)
                        elif process_type == "Regular":
                            self.regular(index, parameters)
                        elif process_type == "Replace":
                            self.replace(index, parameters)
                        elif process_type == "ExtractNum":
                            self.ExtractNum(index, parameters)
                        elif process_type == "Prefix":
                            self.prefix(index, parameters)
                        elif process_type == "Suffix":
                            self.suffix(index, parameters)
                    except Exception as e:
                        raise ValueError(f"参数异常，请输入正确的参数！{process_type}{e}")

    def data_filter_main(self):
        if any(self.cell_filterConfig_list):
            # 单元格过滤
            self.cell_filter()
        if any(self.dataProcessConfig_list):
            # 数据处理
            self.dataProcess()
        if any(self.filterConfig_list):
            # 数据筛选
            self.table_filter()
        if (
            (any(self.cell_filterConfig_list) == False)
            and (any(self.filterConfig_list) == False)
            and (any(self.dataProcessConfig_list) == False)
        ):
            for i in range(len(self.data_values)):
                self.data_json["values"][i]["filterConfig"] = []
                self.data_json["values"][i]["cellFilterConfig"] = []
                self.data_json["values"][i]["dataProcessConfig"] = []

        self.data_table.fillna("")

        return self.data_table

    def get_filtered_data(self):
        """
        获取筛选过滤后数据
        """

        for list_index in range(len(self.hightLightIndex_list)):
            # print(list_index)
            # print(self.data_json["values"][list_index])
            self.data_json["values"][list_index].update(
                {
                    "value": [
                        self.data_values[list_index].get("value")[i] for i in self.hightLightIndex_list[list_index]
                    ],
                    # "highlightRows": self.hightLightIndex_list[list_index],
                }
            )

        if self.dataProcess_state == 1:
            data_list_new = list(map(lambda x: x["value"], self.data_json["values"]))
            for row in range(len(data_list_new)):
                for col in range(len(data_list_new[row])):
                    data_table_text = self.data_table[row].tolist()[col]
                    data_table_text = "" if pd.isnull(data_table_text) else data_table_text
                    if self.produceType == "similar":
                        self.data_values[row]["value"][col].update({"text": data_table_text})
                    else:
                        self.data_values[row]["value"][col] = data_table_text

        return self.data_json

    def get_hightLightIndex(self):
        """
        获取高亮的索引
        """
        return self.hightLightIndex_list


def table_json_merge_values(data_json, values):
    """
    合并获取的 table_list 到 data_json 中组装新的抓取数据
    @:param data_json: 抓取对象
    @:param values: 抓取数据
    """
    logger.info(f"table_data_merge_values data_json: {data_json}")
    logger.info(f"table_data_merge_values values: {values}")
    for index, item in enumerate(data_json["values"]):
        item["value"] = values[index]["value"]
    return data_json


def table_df_to_out(data_json):
    """
    将 data_json 转换成 table 数据用于输出
    @:param data_json: 抓取对象
    """
    produce_type = data_json["produceType"]
    table_head = [item["title"] for item in data_json["values"]]  # 表头
    if produce_type == "table":
        # values: [{"value": ["A", "B", "C"]}, {"value": ["D", "E", "F"]}]
        rows = list(zip(*[item["value"] for item in data_json["values"]]))  # 数据行
    else:
        # values: [{ “value”: [{"text" : “xxx”, "attrs": {}}] }], 按行取出text
        rows_temp = list(zip(*[item["value"] for item in data_json["values"]]))  # 数据行
        rows = [[val_item["text"] for val_item in row] for row in rows_temp]

    df = pd.DataFrame(rows, columns=table_head)
    return df


def table_values_to_table_dict(values, produce_type):
    """
    将 values 转换成 table dict
    """
    produce_type = produce_type
    logger.info(f"table_values_to_table_dict: {values}")
    table_head = [item["title"] for item in values]
    table_data = {}
    max_length = max(len(item["value"]) for item in values)

    if produce_type == "table":
        table_data = {item["title"]: item["value"] for item in values}
    else:
        for item in values:
            val_items = [val_item["text"] for val_item in item["value"]]
            logger.info(f"val_items: {val_items}")
            if len(val_items) < max_length:
                val_items += [""] * (max_length - len(val_items))
            table_data[item["title"]] = val_items
            logger.info(f"table_data: {table_data}")
    table_df = pd.DataFrame(table_data, columns=table_head)
    return table_df.to_dict("list")


def values_to_row_list(values, produce_type):
    """
    将 values 转换成行二维数组
    @:param values: 抓取数组，以列为单元
    @:param produce_type: 抓取类型
    """
    produce_type = produce_type
    logger.info(f"values_to_row_list: {values}")
    table_head = [item["title"] for item in values]
    table_data = {}
    max_length = max(len(item["value"]) for item in values)

    if produce_type == "table":
        table_data = {item["title"]: item["value"] for item in values}
    else:
        for item in values:
            val_items = [val_item for val_item in item["value"]]
            logger.info(f"val_items: {val_items}")
            if len(val_items) < max_length:
                val_items += [{"text": "", "attrs": {}}] * (max_length - len(val_items))
            table_data[item["title"]] = val_items
            logger.info(f"table_data: {table_data}")
    table_df = pd.DataFrame(table_data, columns=table_head)
    return table_df.values.tolist()


def page_values_merge(preValues: list, values: list, produce_type: str):
    """
    将 values 转换成行二维数组
    @:param values: 抓取数组，以列为单元
    @:param produce_type: 抓取类型
    """
    logger.info(f"page_values_merge: {values}")
    # 1, 先补齐values 的每一项内value 的长度
    max_length = max(len(item["value"]) for item in values)
    for item in values:
        if len(item["value"]) < max_length:
            if produce_type == "table":
                item["value"] += [""] * (max_length - len(item["value"]))
            else:
                item["value"] += [{"text": "", "attrs": {}}] * (max_length - len(item["value"]))

    logger.info(f"page_values_merge1: {values}")
    # 2, 将preValues 的value 和 values 的value 合并
    if len(preValues) == 0:
        return values
    else:
        for i in range(len(preValues)):
            preValues[i]["value"] += values[i]["value"]
        return preValues
