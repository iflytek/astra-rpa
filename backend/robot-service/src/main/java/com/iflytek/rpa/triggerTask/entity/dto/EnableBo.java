package com.iflytek.rpa.triggerTask.entity.dto;

import lombok.Data;

@Data
public class EnableBo {
    private String resourceId;
    private Boolean enable;
    private String name;
    private String userId;

    public EnableBo() {}

    public EnableBo(String resourceId, Boolean enable) {
        this.resourceId = resourceId;
        this.enable = enable;
    }

    public EnableBo(String resourceId, String name, String userId) {
        this.resourceId = resourceId;
        this.name = name;
        this.userId = userId;
    }
}
