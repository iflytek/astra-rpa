package com.iflytek.rpa.resource.file.entity.enums;

/**
 * 文件类型枚举
 */
public enum FileType {
    /**
     * 未知类型
     */
    OTHER(0, "未知类型"),

    /**
     * 文本
     */
    TXT(1, "文本"),

    /**
     * WORD
     */
    DOC(2, "WORD"),

    /**
     * PDF
     */
    PDF(3, "PDF");

    private final Integer value;
    private final String comment;

    /**
     * 构造函数
     *
     * @param value   枚举值
     * @param comment 注释说明
     */
    FileType(Integer value, String comment) {
        this.value = value;
        this.comment = comment;
    }

    /**
     * 根据文件名获取文件类型
     *
     * @param filename 文件名
     * @return 文件类型
     */
    public static FileType getFileType(String filename) {
        if (filename == null || filename.trim().isEmpty()) {
            return FileType.OTHER;
        }

        String filenameLower = filename.toLowerCase();
        if (filenameLower.endsWith(".docx") || filenameLower.endsWith(".doc")) {
            return FileType.DOC;
        } else if (filenameLower.endsWith(".pdf")) {
            return FileType.PDF;
        } else if (filenameLower.endsWith(".txt")) {
            return FileType.TXT;
        } else {
            return FileType.OTHER;
        }
    }

    /**
     * 获取枚举值
     *
     * @return 枚举值
     */
    public Integer getValue() {
        return value;
    }

    /**
     * 获取注释说明
     *
     * @return 注释说明
     */
    public String getComment() {
        return comment;
    }
}
