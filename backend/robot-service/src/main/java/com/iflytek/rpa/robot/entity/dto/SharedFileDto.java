package com.iflytek.rpa.robot.entity.dto;

import java.util.List;
import lombok.Data;

@Data
public class SharedFileDto {
    /*
     * fileId
     */
    private String fileId;

    /**
     * 文件名
     */
    private String fileName;
    /**
     * 文件类型
     */
    private Integer fileType;
    /*
     * 标签ID列表（字符串形式，如"1,2,3"）
     */
    private List<Long> tags;
}
