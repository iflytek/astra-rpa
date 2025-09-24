package com.iflytek.rpa.robot.entity.dto;

import java.util.List;
import lombok.Data;
import org.springframework.web.multipart.MultipartFile;

@Data
public class SharedFileUploadDto {

    /**
     * 文件
     */
    private MultipartFile file;

    /*
     * 文件id（新增时设置为null）
     */
    private Long fileId;

    /*
     *标签ids
     */
    private List<Long> tags; // 标签ID列表（字符串形式，如"1,2,3"）
}
