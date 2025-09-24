package com.iflytek.rpa.robot.entity.enums;

import lombok.Getter;

/**
 * 文件类型
 */
@Getter
public enum FileType {
    OTHER("位置类型", 0),
    TXT("文本", 1),
    DOC("WORD", 2),
    PDF("PDF", 3),
    ;

    private final String comment;
    private final Integer value;

    FileType(String comment, Integer value) {
        this.comment = comment;
        this.value = value;
    }

    public static FileType getFileType(String filename) {
        if (filename.endsWith(".docx") || filename.endsWith(".doc")) {
            return FileType.DOC;
        }
        if (filename.endsWith(".pdf")) {
            return FileType.PDF;
        }
        if (filename.endsWith(".txt")) {
            return FileType.TXT;
        }
        return FileType.OTHER;
    }
}
