package com.iflytek.rpa.task.entity.vo;

import com.iflytek.rpa.robot.entity.RobotExecuteRecord;
import java.util.List;
import lombok.Data;

/**
 * 计划任务执行记录列表VO
 *
 * @author jqfang3
 * @since 2025-08-05
 */
@Data
public class TaskRecordListVo {

    /**
     * 任务执行ID
     */
    private String taskExecuteId;

    /**
     * 任务ID
     */
    private String taskId;

    /**
     * 任务名称
     */
    private String taskName;
    /**
     * 任务执行批次
     */
    private Integer count;
    /**
     * 任务类型 手动：manual、定时：schedule、邮件：mail、文件：file、热键：hotKey
     */
    private String taskType;

    /**
     * 任务开始时间
     */
    private String taskStartTime;

    /**
     * 任务结束时间
     */
    private String taskEndTime;

    /**
     * 任务状态：
     * 成功：success、启动失败：start_error、执行失败：exe_error、取消：cancel、执行中：executing
     */
    private String taskExecuteStatus;

    /**
     * 机器人执行记录列表
     */
    private List<RobotExecuteRecord> robotExecuteRecordList;
}
