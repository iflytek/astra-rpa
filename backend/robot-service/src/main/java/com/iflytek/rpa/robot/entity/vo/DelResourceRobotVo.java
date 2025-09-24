package com.iflytek.rpa.robot.entity.vo;

import java.util.List;
import lombok.Data;

@Data
public class DelResourceRobotVo {
    /**
     * 机器人引用关系表
     */
    List<TaskReferInfo> taskReferInfoList;

    /**
     * 机器人Id
     */
    String robotId;
}
