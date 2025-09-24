package com.iflytek.rpa.triggerTask.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class UpdateTaskDto extends InsertTaskDto {
    /**
     * 触发器计划任务id
     */
    @NotBlank
    String taskId;
}
