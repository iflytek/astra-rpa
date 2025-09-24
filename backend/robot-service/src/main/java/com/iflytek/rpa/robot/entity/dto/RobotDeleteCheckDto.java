package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

@Data
public class RobotDeleteCheckDto {
    /**
     * 机器人id
     */
    String robotId;

    /**
     * 创建人id
     */
    String creatorId;
}
