package com.iflytek.rpa.task.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 计划任务机器人列表(ScheduleTaskRobot)实体类
 *
 * @author mjren
 * @since 2024-10-15 14:59:09
 */
@Data
public class ScheduleTaskRobot implements Serializable {
    private static final long serialVersionUID = -98756982211004692L;

    private Long id;
    /**
     * 任务ID
     */
    private String taskId;
    /**
     * 机器人ID
     */
    private String robotId;
    /**
     * 机器人版本
     */
    private Integer version;
    /**
     * 排序, 越小越靠前
     */
    private Integer sort;

    private String tenantId;
    /**
     * 创建者id
     */
    private String creatorId;
    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;
    /**
     * 更新者id
     */
    private String updaterId;
    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;
    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;

    @TableField(exist = false)
    private String robotName;

    @TableField(exist = false)
    private String taskName;

    /**
     * 计划任务机器人配置参数
     */
    private String paramJson;
}
