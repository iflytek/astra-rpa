package com.iflytek.rpa.task.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import java.util.List;
import javax.validation.constraints.NotNull;

/**
 * 调度任务(ScheduleTask)实体类
 *
 * @author makejava
 * @since 2024-09-29 15:33:31
 */
public class ScheduleTask implements Serializable {
    private static final long serialVersionUID = -68626113322208001L;

    private Long id;
    /**
     * 计划任务id
     */
    private String taskId;
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

    private String allRobotName;

    /**
     * 异常处理方式：stop停止  skip跳过
     */
    private String exceptionHandleWay;
    /**
     * 执行模式，循环circular,定时fixed,自定义custom
     */
    private String runMode;
    /**
     * 循环频率，-1为只有一次，3600，，，custom
     */
    private String cycleFrequency;
    /**
     * 循环类型，每1小时，每3小时，，自定义
     */
    private String cycleNum;
    /**
     * 循环单位：minutes, hour
     */
    private String cycleUnit;
    /**
     * 状态：doing执行中 close已结束 ready待执行
     */
    private String status;
    /**
     * 启/禁用
     */
    private Integer enable;
    /**
     * 定时方式,day,month,week（type为“schedule”时生效）
     */
    private String scheduleType;
    /**
     * 定时配置（配置对象）
     */
    private String scheduleRule;
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

    private String tenantId;
    /**
     * 是否排队执行
     */
    private Integer enableQueueExecution;

    /**
     * cron表达式
     */
    private String cronExpression;

    /**
     * cron表达式或者秒数
     */
    private String scheduleConf;
    /**
     * 上次执行时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date lastTime;
    /**
     * 下次执行时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date nextTime;
    /**
     * 创建人ID
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

    private Integer deleted;
    /**
     * 拉取时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date pullTime;

    private String logEnable;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTaskId() {
        return taskId;
    }

    public void setTaskId(String taskId) {
        this.taskId = taskId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getAllRobotName() {
        return allRobotName;
    }

    public void setAllRobotName(String allRobotName) {
        this.allRobotName = allRobotName;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public List<String> getExecuteSequence() {
        return executeSequence;
    }

    public void setExecuteSequence(List<String> executeSequence) {
        this.executeSequence = executeSequence;
    }

    public String getExceptionHandleWay() {
        return exceptionHandleWay;
    }

    public void setExceptionHandleWay(String exceptionHandleWay) {
        this.exceptionHandleWay = exceptionHandleWay;
    }

    public String getRunMode() {
        return runMode;
    }

    public void setRunMode(String runMode) {
        this.runMode = runMode;
    }

    public String getCycleFrequency() {
        return cycleFrequency;
    }

    public void setCycleFrequency(String cycleFrequency) {
        this.cycleFrequency = cycleFrequency;
    }

    public String getCycleNum() {
        return cycleNum;
    }

    public void setCycleNum(String cycleNum) {
        this.cycleNum = cycleNum;
    }

    public String getCycleUnit() {
        return cycleUnit;
    }

    public void setCycleUnit(String cycleUnit) {
        this.cycleUnit = cycleUnit;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Integer getEnable() {
        return enable;
    }

    public void setEnable(Integer enable) {
        this.enable = enable;
    }

    public String getScheduleType() {
        return scheduleType;
    }

    public void setScheduleType(String scheduleType) {
        this.scheduleType = scheduleType;
    }

    public String getScheduleRule() {
        return scheduleRule;
    }

    public void setScheduleRule(String scheduleRule) {
        this.scheduleRule = scheduleRule;
    }

    public Date getStartAt() {
        return startAt;
    }

    public void setStartAt(Date startAt) {
        this.startAt = startAt;
    }

    public Date getEndAt() {
        return endAt;
    }

    public void setEndAt(Date endAt) {
        this.endAt = endAt;
    }

    public String getTenantId() {
        return tenantId;
    }

    public void setTenantId(String tenantId) {
        this.tenantId = tenantId;
    }

    public Integer getEnableQueueExecution() {
        return enableQueueExecution;
    }

    public void setEnableQueueExecution(Integer enableQueueExecution) {
        this.enableQueueExecution = enableQueueExecution;
    }

    public String getCronExpression() {
        return cronExpression;
    }

    public void setCronExpression(String cronExpression) {
        this.cronExpression = cronExpression;
    }

    public String getScheduleConf() {
        return scheduleConf;
    }

    public void setScheduleConf(String scheduleConf) {
        this.scheduleConf = scheduleConf;
    }

    public Date getLastTime() {
        return lastTime;
    }

    public void setLastTime(Date lastTime) {
        this.lastTime = lastTime;
    }

    public Date getNextTime() {
        return nextTime;
    }

    public void setNextTime(Date nextTime) {
        this.nextTime = nextTime;
    }

    public String getCreatorId() {
        return creatorId;
    }

    public void setCreatorId(String creatorId) {
        this.creatorId = creatorId;
    }

    public Date getCreateTime() {
        return createTime;
    }

    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }

    public String getUpdaterId() {
        return updaterId;
    }

    public void setUpdaterId(String updaterId) {
        this.updaterId = updaterId;
    }

    public Date getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(Date updateTime) {
        this.updateTime = updateTime;
    }

    public Integer getDeleted() {
        return deleted;
    }

    public void setDeleted(Integer deleted) {
        this.deleted = deleted;
    }

    public Date getPullTime() {
        return pullTime;
    }

    public void setPullTime(Date pullTime) {
        this.pullTime = pullTime;
    }

    public String getLogEnable() {
        return logEnable;
    }

    public void setLogEnable(String logEnable) {
        this.logEnable = logEnable;
    }
}
