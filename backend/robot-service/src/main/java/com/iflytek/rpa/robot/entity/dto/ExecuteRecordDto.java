package com.iflytek.rpa.robot.entity.dto;

import com.iflytek.rpa.robot.entity.RobotExecuteRecord;
import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ExecuteRecordDto extends RobotExecuteRecord {

    @NotBlank(message = "执行id不能为空")
    private String executeId;

    @NotBlank(message = "机器人id不能为空")
    private String robotId;
    /**
     * 计划任务执行id
     */
    private String taskExecuteId;

    @NotBlank(message = "启动方式不能为空")
    private String mode;

    @NotBlank(message = "执行结果不能为空")
    private String result;

    private String deptIdPath;

    private Integer pageNo;

    private Integer pageSize;

    private String sortBy;

    private String sortType;

    // 新增dispatch相关字段
    /**
     * 是否为dispatch模式，true表示dispatch，false表示原有模式
     */
    private Boolean isDispatch = false;

    /**
     * 机器人版本
     */
    private Integer robotVersion;

    /**
     * dispatch任务执行ID
     */
    private Long dispatchTaskExecuteId;

    /**
     * 终端ID
     */
    private String terminalId;

    /**
     * 错误原因
     */
    private String error_reason;

    /**
     * 执行日志
     */
    private String executeLog;

    /**
     * 视频本地保存路径
     */
    private String videoLocalPath;

    /**
     * 机器人配置参数
     */
    private String paramJson;
}
