import time

from rpaexcel import (
    CopySheetLocationType,
    CopySheetType,
    MoveSheetType,
    SheetInsertType,
    SheetRangeType,
)
from rpaexcel.core import IExcelCore


class SheetCore(IExcelCore):
    excel_obj = None

    @staticmethod
    def _get_ws_obj(excel, sheet_name: str = ""):
        """
        获取工作表对象。
        :param sheet_name: sheet
        :return: ws_obj
        """
        sheet_names = [sheet.Name for sheet in excel.Sheets]
        try:
            sheet_name = int(sheet_name)
            if str(sheet_name) in sheet_names:
                return excel.Worksheets(sheet_name)
            elif sheet_name < 1 or sheet_name > len(sheet_names):
                raise ValueError("输入的sheet名称不存在")
            else:
                return excel.Worksheets(excel.Sheets(sheet_name).Name)
        except ValueError:
            if sheet_name == "":
                return excel.Worksheets(excel.Sheets(1).Name)
            elif sheet_name not in sheet_names:
                raise ValueError("输入的sheet名称不存在")
        return excel.Worksheets(sheet_name)

    @staticmethod
    def get_worksheet_names(excel: object, sheet_range: SheetRangeType = SheetRangeType.ACTIVATED):
        """
        sheet_range: "0":当前sheet页名称; "1":所有sheet页名称
        return:返回所有sheet名
        """
        try:
            if sheet_range == SheetRangeType.ALL:
                sheet_names = [sheet.Name for sheet in excel.Sheets]
            else:
                sheet_names = excel.ActiveSheet.Name
            return sheet_names
        except Exception as err:
            raise err

    @classmethod
    def create_worksheet(
        cls,
        excel: object,
        sheet_name: str,
        insert_type: SheetInsertType = SheetInsertType.FIRST,
        relative_sheet_name: str = "",
    ):
        """
        创建sheet
        excel_obj:excel对象
        sheet_name:sheet名称
        before_sheet_name:在before_sheet_name之前创建sheet
        after_sheet_name:在after_sheet_name之后创建sheet
        """
        sheet_names = cls.get_worksheet_names(excel, SheetRangeType.ALL)
        if sheet_name in sheet_names:
            raise ValueError("新sheet名称已存在")
        if len(sheet_name) >= 31:
            raise ValueError("sheet名称过长,需要小于31个字符")

        if insert_type == SheetInsertType.FIRST:
            new_sheet = excel.Sheets.Add(Before=excel.Sheets(1))
            new_sheet.Name = sheet_name
        elif insert_type == SheetInsertType.LAST:
            new_sheet = excel.Sheets.Add(After=excel.Sheets(len(sheet_names)))
            new_sheet.Name = sheet_name
        else:
            if (not relative_sheet_name) or (relative_sheet_name not in sheet_names):
                raise ValueError("参考sheet名称不存在")
            if insert_type == SheetInsertType.BEFORE:
                new_sheet = excel.Sheets.Add(Before=excel.Sheets(relative_sheet_name))
                new_sheet.Name = sheet_name
            elif insert_type == SheetInsertType.AFTER:
                new_sheet = excel.Sheets.Add(After=excel.Sheets(relative_sheet_name))
                new_sheet.Name = sheet_name

    @classmethod
    def move_worksheet(
        cls,
        excel: object,
        move_sheet: str,
        move_to_sheet: str,
        move_type: MoveSheetType = MoveSheetType.MOVE_AFTER,
    ):
        """
        移动sheet
        move_sheet:要移动的sheet
        move_to_sheet:要移动去的sheet
        excel_obj:excel对象
        """
        try:
            move_sheet_obj = cls._get_ws_obj(excel, move_sheet)

            if move_to_sheet:
                move_to_sheet_obj = cls._get_ws_obj(excel, move_to_sheet)

                if move_type == MoveSheetType.MOVE_AFTER:
                    move_sheet_obj.Move(After=move_to_sheet_obj, Before=None)
                elif move_type == MoveSheetType.MOVE_BEFORE:
                    move_sheet_obj.Move(Before=move_to_sheet_obj, After=None)
            if move_type == MoveSheetType.MOVE_TO_FIRST:
                move_sheet_obj.Move(Before=excel.Worksheets(1), After=None)
            if move_type == MoveSheetType.MOVE_TO_LAST:
                move_sheet_obj.Move(After=excel.Worksheets(excel.Sheets.Count), Before=None)

        except Exception as err:
            raise err

    @classmethod
    def delete_worksheet(cls, excel: object, del_sheet_name: str):
        """
        删除sheet
        excel_obj:excel对象
        del_sheet_name:需要删除sheet名称
        """
        try:
            ws = cls._get_ws_obj(excel, del_sheet_name)
            cls.excel_obj.DisplayAlerts = False
            ws.Delete()
            cls.excel_obj.DisplayAlerts = True
        except Exception as err:
            raise err

    @classmethod
    def rename_worksheet(cls, excel: object, source_sheet_name: str, new_sheet_name: str):
        """
        重命名sheet
        excel_obj:
        new_sheet_name:
        source_sheet_name:
        """
        try:
            sheet_names = cls.get_worksheet_names(excel, SheetRangeType.ALL)
            if new_sheet_name in sheet_names:
                raise ValueError("新sheet名称已存在")
            if len(new_sheet_name) >= 31:
                raise ValueError("sheet名称过长,需要小于31个字符")
            ws = cls._get_ws_obj(excel, source_sheet_name)
            ws.Name = new_sheet_name
        except Exception as err:
            raise err

    @classmethod
    def copy_worksheet(
        cls,
        excel: object,
        source_sheet_name: str,
        new_sheet_name: str,
        location: CopySheetLocationType = CopySheetLocationType.LAST,
        copy_type: CopySheetType = CopySheetType.CURRENT_WORKBOOK,
        other_excel_obj: object = "",
        is_cover: bool = False,
    ):
        """
        excel_obj:excel对象
        source_sheet_name:需复制sheet名称
        new_sheet_name:新复制的sheet名称
        location:位置，Before,After,First,Last,
        copy_type: 复制类型 0 当前工作簿 1 其他工作簿 默认 0
        """
        try:
            sheet_names = cls.get_worksheet_names(excel, sheet_range=SheetRangeType.ALL)

            if copy_type == CopySheetType.CURRENT_WORKBOOK:
                if new_sheet_name in sheet_names and not is_cover:
                    raise ValueError("复制sheet名称已存在")
            else:
                other_sheet_names = cls.get_worksheet_names(other_excel_obj, sheet_range=SheetRangeType.ALL)
                if new_sheet_name in other_sheet_names and not is_cover:
                    raise ValueError("复制sheet名称已存在")
            if len(new_sheet_name) >= 31:
                raise ValueError("sheet名称过长,需要小于31个字符")

            ws_obj = cls._get_ws_obj(excel, source_sheet_name)
            if copy_type == CopySheetType.CURRENT_WORKBOOK:
                if location == CopySheetLocationType.BEFORE:
                    ws_obj.Copy(Before=ws_obj, After=None)
                if location == CopySheetLocationType.AFTER:
                    ws_obj.Copy(After=ws_obj, Before=None)
                if location == CopySheetLocationType.FIRST:
                    ws_obj.Copy(Before=excel.Worksheets(1), After=None)
                if location == CopySheetLocationType.LAST:
                    ws_obj.Copy(After=excel.Worksheets(excel.Sheets.Count), Before=None)

                # 新复制的sheet为当前活动sheet
                if is_cover and new_sheet_name in sheet_names:
                    time.sleep(0.5)
                    excel.Application.DisplayAlerts = False
                    excel.Worksheets(new_sheet_name).Delete()
                    excel.Application.DisplayAlerts = True
                excel.ActiveSheet.Name = new_sheet_name

            else:
                if location == CopySheetLocationType.BEFORE:
                    ws_obj.Copy(
                        Before=other_excel_obj.Worksheets(other_excel_obj.ActiveSheet.Name),
                        After=None,
                    )
                if location == CopySheetLocationType.AFTER:
                    ws_obj.Copy(
                        After=other_excel_obj.Worksheets(other_excel_obj.ActiveSheet.Name),
                        Before=None,
                    )
                if location == CopySheetLocationType.FIRST:
                    ws_obj.Copy(Before=other_excel_obj.Worksheets(1), After=None)
                if location == CopySheetLocationType.LAST:
                    ws_obj.Copy(
                        After=other_excel_obj.Worksheets(other_excel_obj.Sheets.Count),
                        Before=None,
                    )
                # 新复制的sheet为当前活动sheet
                # 原来的逻辑会导致没有同名sheet时勾选覆盖，复制的表会变空
                if is_cover and other_excel_obj.ActiveSheet.Name != new_sheet_name:
                    other_excel_obj.Application.DisplayAlerts = False
                    other_excel_obj.Worksheets(new_sheet_name).Delete()
                    other_excel_obj.Application.DisplayAlerts = True
                other_excel_obj.ActiveSheet.Name = new_sheet_name
        except Exception as err:
            raise err
