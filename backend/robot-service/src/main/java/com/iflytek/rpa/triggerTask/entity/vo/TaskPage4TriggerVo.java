package com.iflytek.rpa.triggerTask.entity.vo;

import java.util.List;
import lombok.Data;

@Data
public class TaskPage4TriggerVo extends TaskPageVo {
    String taskJson; // 计划任务灵活配置参数
    String exceptional;
    Integer timeout;
    Integer queueEnable;
    List<RobotInfoVo> robotInfoList; // 机器人相关部分参数
}
