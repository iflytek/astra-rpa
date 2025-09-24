package com.iflytek.rpa.task.entity.dto;

import com.iflytek.rpa.task.entity.ScheduleTask;
import com.iflytek.rpa.task.entity.bo.TimeTask;
import javax.validation.Valid;
import lombok.Data;

@Data
public class ScheduleTaskDto extends ScheduleTask {

    @Valid
    private TimeTask timeTask;
}
