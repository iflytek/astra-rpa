package com.iflytek.rpa.robot.entity.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class RobotExecutionTrendDataDto {
    /**
     * 机器人id
     */
    @NotBlank(message = "机器人id不能为空")
    String robotId;

    /**
     * 用于趋势图的开始时间
     */
    @NotNull(message = "趋势图开始时间不能为空")
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date startTime;
    /**
     * 用于趋势图的结束时间
     */
    @NotNull(message = "趋势图结束时间不能为空")
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date endTime;
}
