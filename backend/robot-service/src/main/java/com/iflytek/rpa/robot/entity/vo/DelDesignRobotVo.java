package com.iflytek.rpa.robot.entity.vo;

import java.util.List;
import lombok.Data;

@Data
public class DelDesignRobotVo {
    // 机器人删除情况分类：1： 设计器 ，2：设计器 执行器，3：设计器 执行期 被计划任务引用
    Integer situation;

    // 机器人引用关系表
    List<TaskReferInfo> taskReferInfoList;

    // 机器人Id
    String robotId;
}
