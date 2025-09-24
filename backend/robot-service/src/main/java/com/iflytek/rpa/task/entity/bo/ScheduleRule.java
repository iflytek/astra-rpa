package com.iflytek.rpa.task.entity.bo;

import lombok.Data;

@Data
public class ScheduleRule {
    private Integer dayOfWeek; // 定时：周几

    private Integer year; // 定时：年

    private Integer month; // 定时：月

    private Integer date; // 定时：日

    private Integer hour; // 定时：时

    private Integer minute; // 定时：分

    private Integer second; // 定时：秒
}
