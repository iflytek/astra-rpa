package com.iflytek.rpa.robot.entity.vo;

import java.util.List;
import lombok.Data;

@Data
public class DelExecuteRobotVo {
    // 机器人删除情况分类：1：执行器，3：执行器 被计划任务引用  为了前端复用
    Integer situation;

    // 机器人引用关系表
    List<TaskReferInfo> taskReferInfoList;

    // 机器人Id
    String robotId;
}
