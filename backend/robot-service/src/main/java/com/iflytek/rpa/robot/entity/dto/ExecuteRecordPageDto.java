package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

@Data
public class ExecuteRecordPageDto {
    Integer pageSize = 10;

    Integer pageNo = 1;

    String robotId;
}
