package com.iflytek.rpa.task.entity.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

/**
 * 计划任务执行记录列表DTO
 *
 * @author jqfang3
 * @since 2025-08-05
 */
@Data
public class ScheduleTaskRecordDto {
    /**
     * 计划任务名称
     */
    private String taskName;
    /**
     * 开始日期
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date startDate;
    /**
     * 结束日期
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date endDate;
    /**
     * 任务状态枚举:成功:success、启动失败:start_error、执行失败:exe_error、取消:cancel、执行中:executing
     */
    private String status;
    /**
     * 任务类型：手动：manual、定时：schedule、邮件：mail、文件：file、热键：hotKey
     */
    private String taskType;

    private Integer pageNo;

    private Integer pageSize;

    /**
     * 排序默认:开始时间
     */
    private String sortBy = "startTime";
    /**
     * 默认降序
     */
    private String sortType = "desc";

    /**
     * 用户ID
     */
    private String userId;

    /**
     * 租户ID
     */
    private String tenantId;
}
