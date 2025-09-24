package com.iflytek.rpa.task.entity.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import java.util.List;
import lombok.Data;

@Data
public class NextTaskDto {

    private String taskId;

    private String taskName;

    private List<String> robotIdList;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date nextTime;

    private String exceptionHandleWay;
}
