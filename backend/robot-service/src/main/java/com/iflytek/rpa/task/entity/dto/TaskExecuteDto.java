package com.iflytek.rpa.task.entity.dto;

import com.iflytek.rpa.robot.entity.RobotExecuteRecord;
import com.iflytek.rpa.task.entity.ScheduleTaskExecute;
import java.util.List;
import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class TaskExecuteDto extends ScheduleTaskExecute {

    @NotBlank(message = "任务id不能为空")
    private String taskId;

    private List<RobotExecuteRecord> robotExecuteRecordList;

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
     * dispatch任务ID
     */
    private Long dispatchTaskId;

    /**
     * dispatch任务执行ID
     */
    private Long dispatchTaskExecuteId;

    /**
     * 终端ID
     */
    private String terminalId;
}
