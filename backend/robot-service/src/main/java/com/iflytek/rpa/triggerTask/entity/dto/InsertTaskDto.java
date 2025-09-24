package com.iflytek.rpa.triggerTask.entity.dto;

import com.iflytek.rpa.task.entity.dto.RobotInfo;
import java.util.List;
import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class InsertTaskDto {
    /**
     * 触发器计划任务名称
     */
    @NotBlank
    private String name;

    /**
     * 报错如何处理：跳过 jump、中止 stop
     */
    @NotBlank
    private String exceptional;

    /**
     * 是否启用 1 启用 ；0 不启用
     */
    private Integer enable; // 是否启用 1 启用 ；0 不启用

    /**
     * 任务类型：定时:schedule、mail、file、hotKey、manual:
     */
    @NotBlank
    private String taskType;

    /**
     * 超时时间
     */
    private Integer timeout;

    /**
     * 构建计划任务的灵活参数
     */
    @NotBlank
    private String taskJson;

    /**
     * 机器人执行序列
     */
    private List<RobotInfo> robotInfoList;

    /**
     * 是否启用排队 1:启用 0:不启用
     */
    private Integer queueEnable;
}
