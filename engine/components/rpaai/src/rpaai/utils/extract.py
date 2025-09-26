class FileExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text(self) -> str:
        """
        提取文件文本内容

        :return:
        """
        file_extension = self.file_path.split(".")[-1]
        if file_extension.lower() == "pdf":
            text_content = self.extract_pdf(self.file_path)
        elif file_extension.lower() in ["docx", "doc"]:
            text_content = self.extract_docx(self.file_path)
        elif file_extension.lower() == "txt":
            text_content = open(self.file_path).read()
        else:
            raise ValueError("不支持的文件扩展类型: " + file_extension)
        return text_content

    @staticmethod
    def extract_pdf(path: str) -> str:
        """
        提取 pdf 文本内容

        :param path:
        :return:
        """
        import pypdf

        pdf_reader = pypdf.PdfReader(path)
        return "\n".join([pdf_reader.pages[page_num].extract_text() for page_num in range(len(pdf_reader.pages))])

    @staticmethod
    def extract_docx(path: str) -> str:
        """
        提取 docx 文本内容

        :param path:
        :return:
        """
        from docx import Document
        from docx.table import Table
        from docx.text.paragraph import Paragraph

        doc = Document(path)
        full_text = []
        # 通过文档的 XML 结构按顺序处理
        for element in doc.element.body:
            if element.tag.endswith("p"):  # 段落
                full_text.append(Paragraph(element, doc).text)
            elif element.tag.endswith("tbl"):  # 表格
                table = Table(element, doc)
                for row in table.rows:
                    row_text = " | ".join(cell.text for cell in row.cells)
                    full_text.append(row_text)
        return "\n".join(full_text)
