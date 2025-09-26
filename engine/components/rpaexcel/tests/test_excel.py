from unittest import TestCase

from rpaexcel import (
    ApplicationType,
    CloseRangeType,
    ColumnDirectionType,
    ColumnType,
    EnhancedInsertType,
    FileExistenceType,
    ImageSizeType,
    PasteType,
    ReadRangeType,
    RowDirectionType,
    RowType,
    SaveType,
    SaveType_ALL,
    SearchRangeType,
    SheetInsertType,
    SheetRangeType,
)
from rpaexcel.excel import Excel


class TestExcel(TestCase):
    def setUp(self):
        self.excel = Excel()
        self.open_excel = self.excel.open_excel(
            file_path=r"C:\RPA\excel——test.xlsx",
            default_application=ApplicationType.WPS,
        )

    def test_open_excel(self):
        excel = Excel()
        excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")

    def test_get_exist_excel(self):
        excel = Excel()
        print(excel.get_excel(file_name="公众号提取").Name)

    def test_create_excel(self):
        excel = Excel()
        excelwork = excel.create_excel(
            file_path=r"C:\RPA",
            visible_flag=False,
            file_name="excel——test",
            exist_handle_type=FileExistenceType.OVERWRITE,
        )
        print(excelwork)

    def test_save_excel(self):
        excel = Excel()
        excel_obj = excel.get_excel(file_name="llj")
        excel.save_excel(excel=excel_obj)

    def test_close_excel(self):
        excel_obj = self.excel.get_excel(file_name="eee")
        self.excel.close_excel(
            close_range_flag=CloseRangeType.ALL,
            excel=excel_obj,
            pkill_flag=True,
            save_type_all=SaveType_ALL.ABORT,
            save_type_one=SaveType.ABORT,
        )

    def test_edit_excel(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        excel.edit_excel(
            excel_obj,
            sheet_name="Sheet1",
            start_col="A",
            start_row=1,
            edit_range="area",
            value=[[1, 21, 4], [2, 4, 5]],
        )
        # _ = excel.save_excel(excel=edit_excel)

    def test_read_excel(self):
        excel = Excel()
        excel_obj = excel.get_excel(file_name="111")
        # contents = excel.read_excel(excel=excel_obj, sheet_name='Sheet1', read_range='row', row=2, read_display=True, trim_spaces=True, replace_none=True)
        # contents = excel.read_excel(excel=excel_obj, sheet_name='Sheet1', read_range='cell', cell='F2',
        #                             trim_spaces=True, replace_none=True)
        contents = Excel().read_excel(
            excel=excel_obj,
            read_range=ReadRangeType.ALL,
            replace_none=True,
            read_display=False,
        )
        print(contents)

    def test_design_cell_type(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        excel.design_cell_type(
            excel=excel_obj,
            design_type=3,
            range_position="A1:B9",
            sheet_name="Sheet1",
            font_type="粗体",
            font_name="宋体",
            font_color=[127, 0, 255],
        )

    def test_copy_and_paste(self):
        data = self.excel.copy_excel(
            excel=self.open_excel,
            range_position="A1:B4",
            copy_range_type=ReadRangeType.AREA,
        )
        print(type(data))
        new_excel = self.excel.paste_excel(excel=self.open_excel, start_location="H2", paste_type=PasteType.PASTE_VALUE)

    def test_delete_cell(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        new_excel = excel.delete_excel_cell(excel=excel_obj, delete_range_excel="cell", coordinate="A1")
        return new_excel

    def test_clear_content(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        new_excel = excel.clear_excel_content(
            excel=excel_obj,
            sheet_name="Sheet1",
            cell_location="B2",
            clear_type="all",
            select_type="cell",
        )
        return new_excel

    def test_insert_row_or_column(self):
        self.excel.insert_excel_row_or_column(
            excel=self.open_excel,
            row="1",
            insert_num=3,
            insert_content=[[1, 2, 3, 6, 6, 6], [2, 2, 3]],
            row_direction=RowDirectionType.LOWER,
            insert_type=EnhancedInsertType.ROW,
            col=1,
            col_direction=ColumnDirectionType.RIGHT,
            blank_rows=True,
        )

    def test_get_row_num(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        row_num = excel.get_excel_row_num(excel=excel_obj)
        col_num = excel.get_excel_col_num(excel=excel_obj)
        print(row_num)
        print(col_num)
        return row_num, col_num

    def test_add_line_write(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        new_excel = excel.excel_add_line_write(
            excel=excel_obj,
            sheet_name="Sheet1",
            write_data=["测试数据", "测试数据2", "测试数据3"],
        )
        return new_excel

    def test_cell_color(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        color = excel.excel_get_cell_color(excel=excel_obj, sheet_name="Sheet1", coordinate="B1")
        print(color)

    def test_merge_split(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        new_excel = excel.merge_split_excel_cell(
            excel=excel_obj, sheet_name="Sheet1", merge_cell_range="A1:B2", job_type=1
        )
        new_excel2 = excel.merge_split_excel_cell(
            excel=excel_obj, sheet_name="Sheet1", split_cell_range="A1:B1", job_type=0
        )
        return new_excel2

    def test_move_excel_worksheet(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        new_excel = excel.move_excel_worksheet(excel=excel_obj, move_sheet_name="Sheet1", move_location_index=2)
        return new_excel

    def test_delete_excel_worksheet(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        new_excel = excel.delete_excel_worksheet(excel=excel_obj, del_sheet_name="Sheet2")
        return new_excel

    def test_rename_excel_worksheet(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        new_excel = excel.rename_excel_worksheet(excel=excel_obj, source_sheet_name="Sheet1", new_sheet_name="111a")
        return new_excel

    def test_get_excel_sheet_names(self):
        sheet_names = self.excel.get_excel_worksheet_names(excel=self.open_excel, sheet_range=SheetRangeType.ALL)
        print(sheet_names)

    def test_copy_excel_sheet(self):
        excel = Excel()
        excel_obj = excel.open_excel(file_path=r"C:\Users\xcwang31\Desktop\llj.xlsx")
        new_excel = excel.copy_excel_worksheet(
            excel=excel_obj,
            source_sheet_name="Sheet1",
            new_sheet_name="111a",
            location="Before",
        )
        return new_excel

    def test_search_excel_content(self):
        # result = self.excel.search_excel_content(excel=self.open_excel, find_str = "1", search_range=SearchRangeType.ALL, lookup_range_excel=SearchSheetType.ALL, sheet_name="Sheet3",
        #                                          case_flag=True, output_type=SearchResultType.CELL, replace_flag=True, replace_str="b", exact_match=True)
        result = self.excel.search_and_replace_excel_content(excel=self.open_excel, find_str="1")
        print(result)

    def test_insert_image(self):
        self.excel.insert_pic(
            self.open_excel,
            sheet_name="Sheet1",
            insert_pos="A8:C10",
            pic_path=r"C:\Users\zyzhou23\Desktop\老拾取.png",
            pic_width=100,
            pic_height=100,
            pic_size_type=ImageSizeType.AUTO,
            pic_scale=0.3,
        )
        self.excel.insert_pic(
            self.open_excel,
            sheet_name="Sheet1",
            insert_pos="A18:C20",
            pic_path=r"C:\Users\zyzhou23\Pictures\11, .jpg",
            pic_width=100,
            pic_height=100,
            pic_size_type=ImageSizeType.AUTO,
            pic_scale=0.3,
        )

    def test_first_rowcol(self):
        print(self.excel.get_excel_first_available_col(excel=self.open_excel))
        # print(self.excel.get_excel_first_available_row(excel=self.open_excel))
        # print(self.excel.get_excel_row_num(excel=self.open_excel))
        # print(self.excel.get_excel_col_num(excel=self.open_excel))

    def test_loop(self):
        print(
            self.excel.loop_excel_content(
                excel=self.open_excel,
                select_type=SearchRangeType.COLUMN,
                start_col="A",
                end_col="C",
            )
        )

    def test_insert_sheet(self):
        self.excel.add_excel_worksheet(
            excel=self.open_excel,
            sheet_name="awawa",
            insert_type=SheetInsertType.AFTER,
            relative_sheet_name="中信银行",
        )

    def test_get_col(self):
        col_num = self.excel.get_excel_col_num(self.open_excel, get_row_type=RowType.ONE_ROW, row="2")
        print(col_num)

    def test_get_row(self):
        row_num = self.excel.get_excel_row_num(self.open_excel, get_col_type=ColumnType.ONE_COLUMN, col="-1")
        print(row_num)

    def test_loop_excel_content(self):
        content = self.excel.loop_excel_content(
            self.open_excel,
            select_type=SearchRangeType.COLUMN,
            start_row="1",
            end_row="2",
            start_col="1",
            end_col="3",
        )
        print(content)
