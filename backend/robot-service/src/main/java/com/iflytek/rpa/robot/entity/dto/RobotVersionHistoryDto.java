package com.iflytek.rpa.robot.entity.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-07-15 14:16
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class RobotVersionHistoryDto {

    private Integer version;

    private String updateLog;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;
}
