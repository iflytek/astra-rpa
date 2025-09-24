package com.iflytek.rpa.base.entity.dto;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDIT_PAGE;

import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-04-17 10:45
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class QueryParamDto {

    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    /**
     * 运行位置，默认编辑页，EDIT_PAGE编辑页,PROJECT_LIST设计器列表页,EXECUTOR执行器机器人列表页,CRONTAB触发器（本地计划任务）
     */
    private String mode = EDIT_PAGE;

    private String processId;

    /**
     * schedule_task_robot表的id，一个机器人A在计划任务1中可以出现多次
     */
    private Long taskRobotUniqueId;
    /**
     * 调度模式计划任务机器人版本
     */
    private Integer robotVersion;
}
