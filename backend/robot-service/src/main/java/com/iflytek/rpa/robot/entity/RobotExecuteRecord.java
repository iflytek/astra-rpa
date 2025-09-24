package com.iflytek.rpa.robot.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 云端机器人执行记录表(RobotExecuteRecord)实体类
 *
 * @author makejava
 * @since 2024-09-29 15:34:14
 */
@Data
public class RobotExecuteRecord implements Serializable {
    private static final long serialVersionUID = 930070558482150308L;
    /**
     * 主键id
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private String executeId;

    /**
     * 机器人id
     */
    private String robotId;
    /**
     * 机器人名称
     */
    private String robotName;
    /**
     * 机器人版本号
     */
    private Integer robotVersion;
    /**
     * 开始时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date startTime;
    /**
     * 结束时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date endTime;
    /**
     * 执行耗时 单位秒
     */
    private Long executeTime;
    /**
     * 枚举: startBtn,schedule,commander枚举备注: 执行方式目前主要是三种（1）点击运行按钮执行机器人（2）计划任务执行的机器人（3）commander远端执行机器人
     */
    private String mode;
    /**
     * 计划任务执行id
     */
    private String taskExecuteId;
    /**
     * 执行结果
     * robotFail:失败
     * robotSuccess:成功
     * robotCancel:取消(中止)
     * robotExecute:正在执行
     */
    private String result;
    /**
     * 错误原因
     */
    private String errorReason;
    /**
     * 日志内容
     */
    private String executeLog;
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

    private String tenantId;

    private String videoLocalPath;

    private String terminalId;

    @TableField(exist = false)
    private String taskName;
}
