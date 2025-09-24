package com.iflytek.rpa.robot.entity.vo;

import java.util.List;
import lombok.Data;

@Data
public class TaskReferInfo {

    // taskId
    String taskId;

    // 引用该执行器的计划任务名称
    String taskName;

    // 执行器名称；
    List<String> robotNames;

    // 高亮index位
    List<Integer> highIndex;
}
