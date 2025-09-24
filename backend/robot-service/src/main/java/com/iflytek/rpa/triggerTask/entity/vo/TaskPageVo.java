package com.iflytek.rpa.triggerTask.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

@Data
public class TaskPageVo {
    String taskId; // 触发器计划任务id
    String name; // 触发器计划任务名称
    String robotNames; // 机器人名称，用逗号隔开

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    Date createTime;

    String taskType; // 定时:schedule、邮件mail、文件file、热键hotKey
    Integer enable; // 是否启用 1 启用 ；0 不启用
    String taskJson; // 计划任务灵活配置参数
}
