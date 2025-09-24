package com.iflytek.rpa.task.entity.dto;

import java.util.List;
import lombok.Data;

@Data
public class ScheduleTaskRecordDeleteDto {
    List<String> taskExecuteIdList;
}
