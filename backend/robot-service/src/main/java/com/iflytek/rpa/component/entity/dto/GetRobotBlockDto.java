package com.iflytek.rpa.component.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class GetRobotBlockDto {
    /**
     * 机器人id
     */
    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    /**
     * 发起请求的位置
     */
    @NotBlank(message = "mode不能为空")
    private String mode;

    /**
     * 机器人版本号
     */
    private Integer robotVersion;
}
