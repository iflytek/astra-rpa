package com.iflytek.rpa.robot.entity.dto;

import java.util.List;
import javax.validation.constraints.NotNull;
import lombok.Data;

/**
 * 共享文件批量删除DTO
 */
@Data
public class SharedFileBatchDeleteDto {
    /**
     * 共享文件ID List
     */
    @NotNull(message = "共享文件ID-List不能为空")
    private List<String> fileIds;
}
