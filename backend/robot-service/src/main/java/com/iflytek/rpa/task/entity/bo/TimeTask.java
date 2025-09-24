package com.iflytek.rpa.task.entity.bo;

import javax.validation.constraints.NotBlank;
import lombok.Data;
import org.hibernate.validator.constraints.Length;

@Data
public class TimeTask {
    /**
     * 执行模式，循环circular,定时fixed,自定义custom
     */
    @NotBlank(message = "执行方式不能为空")
    private String runMode;
    /**
     * 循环频率，-1为只有一次，3600，，，custom
     */
    @Length(max = 20, message = "循环频率长度不能超过20")
    private String cycleFrequency;
    /**
     * 循环类型，每1小时，每3小时，，自定义
     */
    @Length(max = 20, message = "自定义时长过长")
    private String cycleNum;
    /**
     * 循环单位：minutes, hour
     */
    private String cycleUnit;

    private String scheduleType;

    private ScheduleRule scheduleRule;

    /**
     * cron表达式
     */
    private String cronExpression;
}
