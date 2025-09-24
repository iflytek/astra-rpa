package com.iflytek.rpa.robot.entity.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class RobotExecutionDataDto {
    /**
     * 机器人ID
     */
    @NotBlank(message = "机器人ID不能为空")
    private String robotId;
    /**
     * 截止时间
     */
    @NotNull(message = "截止时间不能为空")
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date deadline; // 截止时间
}
