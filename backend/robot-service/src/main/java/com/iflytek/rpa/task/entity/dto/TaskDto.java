package com.iflytek.rpa.task.entity.dto;

import lombok.Data;

@Data
public class TaskDto {

    private String userId;

    private String name;

    private Long pageNo;

    private Long pageSize;

    // 如update_time
    private String sortBy;

    // desc或asc
    private String sortType;
}
