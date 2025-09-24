package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

@Data
public class RobotDeleteDto {
    /**
     * 机器人id
     */
    String robotId;
    /**
     * 多个引用该机器人的计划任务id，用逗号隔开
     */
    String taskIds;
    /**
     * 创建人id
     */
    String creatorId;
}
