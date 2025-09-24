package com.iflytek.rpa.task.entity.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.iflytek.rpa.task.entity.bo.TimeTask;
import java.util.Date;
import java.util.List;
import javax.validation.Valid;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class TaskInfoDto {
    /**
     * 计划任务id
     */
    private String taskId;

    private String taskType = "taskTime";

    /**
     * 任务名称
     */
    @NotNull(message = "任务名称不能为空")
    private String name;
    /**
     * 描述
     */
    private String description;
    /**
     * 执行机器人序列
     */
    //    @JsonSerialize(using = ListRobotJsonSerializer.class)
    private List<String> executeSequence;

    /**
     * 异常处理方式：stop停止  skip跳过
     */
    private String exceptionHandleWay;

    /**
     * 开始时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm", timezone = "GMT+8")
    private Date startAt;
    /**
     * 结束时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm", timezone = "GMT+8")
    private Date endAt;

    @Valid
    private TimeTask timeTask;
}
